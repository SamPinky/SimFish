import json
import h5py
from datetime import datetime
import os

import numpy as np
import tensorflow.compat.v1 as tf

from Environment.naturalistic_environment import NaturalisticEnvironment
from Environment.controlled_stimulus_environment import ControlledStimulusEnvironment
from Network.q_network import QNetwork
from Tools.make_gif import make_gif

tf.logging.set_verbosity(tf.logging.ERROR)


def assay_target(trial, learning_params, environment_params, total_steps, episode_number, memory_fraction):
    service = AssayService(model_name=trial["Model Name"],
                           trial_number=trial["Trial Number"],
                           assay_config_name=trial["Assay Configuration Name"],
                           learning_params=learning_params,
                           environment_params=environment_params,
                           total_steps=total_steps,
                           episode_number=episode_number,
                           assays=trial["Assays"],
                           realistic_bouts=trial["Realistic Bouts"],
                           memory_fraction=memory_fraction,
                           using_gpu=trial["Using GPU"],
                           set_random_seed=trial["set random seed"]
                           )

    service.run()


class AssayService:

    def __init__(self, model_name, trial_number, assay_config_name, learning_params, environment_params, total_steps,
                 episode_number, assays, realistic_bouts, memory_fraction, using_gpu, set_random_seed):
        """
        Runs a set of assays provided by the run configuraiton.
        """

        # Set random seed
        if set_random_seed:
            np.random.seed(404)

        # Names and Directories
        self.model_id = f"{model_name}-{trial_number}"
        self.model_location = f"./Training-Output/{self.model_id}"
        self.data_save_location = f"./Assay-Output/{self.model_id}"

        # Configurations
        self.assay_configuration_id = assay_config_name
        self.learning_params = learning_params
        self.environment_params = environment_params
        self.assays = assays

        # Basic Parameters
        self.using_gpu = using_gpu
        self.realistic_bouts = realistic_bouts
        self.memory_fraction = memory_fraction

        # Network Parameters
        self.saver = None
        self.network = None
        self.init = None
        self.sess = None

        # Simulation
        self.simulation = NaturalisticEnvironment(self.environment_params, self.realistic_bouts)
        self.step_number = 0

        # Data
        self.metadata = {
            "Total Episodes": episode_number,
            "Total Steps": total_steps,
        }
        self.frame_buffer = []
        self.assay_output_data_format = None
        self.assay_output_data = []
        self.output_data = {}
        self.episode_summary_data = None

        # Hacky fix for h5py problem:
        self.last_position_dim = self.environment_params["prey_num"]
        self.stimuli_data = []

    def create_network(self):
        internal_states = sum([1 for x in [self.environment_params['hunger'], self.environment_params['stress']] if x is True]) + 1

        cell = tf.nn.rnn_cell.LSTMCell(num_units=self.learning_params['rnn_dim'], state_is_tuple=True)
        network = QNetwork(simulation=self.simulation,
                           rnn_dim=self.learning_params['rnn_dim'],
                           rnn_cell=cell,
                           my_scope='main',
                           num_actions=self.learning_params['num_actions'],
                           internal_states=internal_states,
                           learning_rate=self.learning_params['learning_rate'],
                           extra_layer=self.learning_params['extra_rnn'])
        return network

    def create_testing_environment(self, assay):
        """
        Creates the testing environment as specified  by apparatus mode and given assays.
        :return:
        """
        if assay["stimulus paradigm"] == "Projection":
            self.simulation = ControlledStimulusEnvironment(self.environment_params, assay["stimuli"],
                                                            self.realistic_bouts,
                                                            tethered=assay["Tethered"],
                                                            set_positions=assay["set positions"],
                                                            random=assay["random positions"],
                                                            moving=assay["moving"],
                                                            reset_each_step=assay["reset"],
                                                            reset_interval=assay["reset interval"],
                                                            background=assay["background"]
                                                            )
        elif assay["stimulus paradigm"] == "Naturalistic":
            self.simulation = NaturalisticEnvironment(self.environment_params, self.realistic_bouts, collisions=assay["collisions"])
        else:
            self.simulation = NaturalisticEnvironment(self.environment_params, self.realistic_bouts)

    def run(self):
        if self.using_gpu:
            options = tf.GPUOptions(per_process_gpu_memory_fraction=self.memory_fraction)
        else:
            options = None

        if options:
            with tf.Session(config=tf.ConfigProto(gpu_options=options)) as self.sess:
                self._run()
        else:
            with tf.Session() as self.sess:
                self._run()

    def _run(self):
        self.network = self.create_network()
        self.saver = tf.train.Saver(max_to_keep=5)
        self.init = tf.global_variables_initializer()
        checkpoint = tf.train.get_checkpoint_state(self.model_location)
        self.saver.restore(self.sess, checkpoint.model_checkpoint_path)
        print("Model loaded")
        for assay in self.assays:
            if assay["ablations"]:
                self.ablate_units(assay["ablations"])
            self.create_output_data_storage(assay)
            self.create_testing_environment(assay)
            self.perform_assay(assay)
            if assay["save stimuli"]:
                self.save_stimuli_data(assay)
            # self.save_assay_results(assay)
            self.save_hdf5_data(assay)
        self.save_metadata()
        self.save_episode_data()

    def create_output_data_storage(self, assay):
        self.output_data = {key: [] for key in assay["recordings"]}
        self.output_data["step"] = []

    def ablate_units(self, unit_indexes):
        for unit in unit_indexes:
            if unit < 256:
                output = self.sess.graph.get_tensor_by_name('mainaw:0')
                new_tensor = output.eval()
                new_tensor[unit] = np.array([0 for i in range(10)])
                self.sess.run(tf.assign(output, new_tensor))
            else:
                output = self.sess.graph.get_tensor_by_name('mainvw:0')
                new_tensor = output.eval()
                new_tensor[unit-256] = np.array([0])
                self.sess.run(tf.assign(output, new_tensor))

    def perform_assay(self, assay):
        self.assay_output_data_format = {key: None for key in assay["recordings"]}

        self.simulation.reset()
        rnn_state = (np.zeros([1, self.network.rnn_dim]), np.zeros([1, self.network.rnn_dim]))  # Reset RNN hidden state
        sa = np.zeros((1, 128))

        o, r, internal_state, d, self.frame_buffer = self.simulation.simulation_step(action=3,
                                                                                     frame_buffer=self.frame_buffer,
                                                                                     save_frames=True,
                                                                                     activations=(sa,))
        a = 0
        self.step_number = 0
        while self.step_number < assay["duration"]:
            if assay["reset"] and self.step_number % assay["reset interval"] == 0:
                rnn_state = (np.zeros([1, self.network.rnn_dim]), np.zeros([1, self.network.rnn_dim]))  # Reset RNN hidden state
            self.step_number += 1

            o, a, r, internal_state, o1, d, rnn_state = self.step_loop(o=o, internal_state=internal_state,
                                                                       a=a, rnn_state=rnn_state)
            o = o1

            if d:
                break

    def step_loop(self, o, internal_state, a, rnn_state):
        chosen_a, updated_rnn_state, rnn2_state, sa, sv, conv1l, conv2l, conv3l, conv4l, conv1r, conv2r, conv3r, conv4r, o2 = \
            self.sess.run(
                [self.network.predict, self.network.rnn_state, self.network.rnn_state2, self.network.streamA, self.network.streamV,
                 self.network.conv1l, self.network.conv2l, self.network.conv3l, self.network.conv4l,
                 self.network.conv1r, self.network.conv2r, self.network.conv3r, self.network.conv4r,
                 [self.network.ref_left_eye, self.network.ref_right_eye],
                 ],
                feed_dict={self.network.observation: o,
                           self.network.internal_state: internal_state,
                           self.network.prev_actions: [a],
                           self.network.trainLength: 1,
                           self.network.state_in: rnn_state,
                           self.network.batch_size: 1,
                           self.network.exp_keep: 1.0})
        chosen_a = chosen_a[0]
        o1, given_reward, internal_state, d, self.frame_buffer = self.simulation.simulation_step(action=chosen_a,
                                                                                                 frame_buffer=self.frame_buffer,
                                                                                                 save_frames=True,
                                                                                                 activations=(sa,))
        fish_angle = self.simulation.fish.body.angle

        if not self.simulation.sand_grain_bodies:
            sand_grain_positions = [self.simulation.sand_grain_bodies[i].position for i, b in
                                    enumerate(self.simulation.sand_grain_bodies)]
            sand_grain_positions = [[i[0], i[1]] for i in sand_grain_positions]
        else:
            sand_grain_positions = [[10000, 10000]]

        if self.simulation.prey_bodies:
            # TODO: Note hacky fix which may want to clean up later.
            prey_positions = [prey.position for prey in self.simulation.prey_bodies]
            prey_positions = [[i[0], i[1]] for i in prey_positions]
            while True:
                if len(prey_positions) < self.last_position_dim:
                    prey_positions = np.append(prey_positions, [[10000, 10000]], axis=0)
                else:
                    break

            self.last_position_dim = len(prey_positions)

        else:
            prey_positions = np.array([[10000, 10000]])

        if self.simulation.predator_body is not None:
            predator_position = self.simulation.predator_body.position
            predator_position = np.array([predator_position[0], predator_position[1]])
        else:
            predator_position = np.array([10000, 10000])

        if self.simulation.vegetation_bodies is not None:
            vegetation_positions = [self.simulation.vegetation_bodies[i].position for i, b in enumerate(self.simulation.vegetation_bodies)]
            vegetation_positions = [[i[0], i[1]] for i in vegetation_positions]
        else:
            vegetation_positions = [[10000, 10000]]

        if not self.learning_params["extra_rnn"]:
            rnn2_state = [0.0]

        # Saving step data
        possible_data_to_save = self.package_output_data(o1, o2, chosen_a, sa, updated_rnn_state,
                                                         rnn2_state,
                                                         self.simulation.fish.body.position,
                                                         self.simulation.prey_consumed_this_step,
                                                         self.simulation.predator_body,
                                                         conv1l, conv2l, conv3l, conv4l, conv1r, conv2r, conv3r, conv4r,
                                                         prey_positions,
                                                         predator_position,
                                                         sand_grain_positions,
                                                         vegetation_positions,
                                                         fish_angle,
                                                         )
        for key in self.assay_output_data_format:
            self.output_data[key].append(possible_data_to_save[key])
        self.output_data["step"].append(self.step_number)

        return o, chosen_a, given_reward, internal_state, o1, d, updated_rnn_state

    def save_hdf5_data(self, assay):
        if assay["save frames"]:
            make_gif(self.frame_buffer,
                     f"{self.data_save_location}/{self.assay_configuration_id}-{assay['assay id']}.gif",
                     duration=len(self.frame_buffer) * self.learning_params['time_per_step'], true_image=True)
        self.frame_buffer = []

        # absolute_path = '/home/sam/PycharmProjects/SimFish/Assay-Output/new_differential_prey_ref-3' + f'/{self.assay_configuration_id}.h5'
        # hdf5_file = h5py.File(absolute_path, "a")
        hdf5_file = h5py.File(f"{self.data_save_location}/{self.assay_configuration_id}.h5", "a")

        try:
            assay_group = hdf5_file.create_group(assay['assay id'])
        except ValueError:
            assay_group = hdf5_file.get(assay['assay id'])

        if "prey_positions" in self.assay_output_data_format.keys():
            self.output_data["prey_positions"] = np.stack(self.output_data["prey_positions"])

        for key in self.output_data:
            try:
                # print(self.output_data[key])
                assay_group.create_dataset(key, data=np.array(self.output_data[key]))  # TODO: Compress data.
            except RuntimeError:
                del assay_group[key]
                assay_group.create_dataset(key, data=np.array(self.output_data[key]))  # TODO: Compress data.
        hdf5_file.close()

    def save_episode_data(self):
        self.episode_summary_data = {
            "Prey Caught": self.simulation.prey_caught,
            "Predators Avoided": self.simulation.predators_avoided,
            "Sand Grains Bumped": self.simulation.sand_grains_bumped,
            "Steps Near Vegetation": self.simulation.steps_near_vegetation
        }
        with open(f"{self.data_save_location}/{self.assay_configuration_id}-summary_data.json", "w") as output_file:
            json.dump(self.episode_summary_data, output_file)
        self.episode_summary_data = None

    def save_stimuli_data(self, assay):
        with open(f"{self.data_save_location}/{self.assay_configuration_id}-{assay['assay id']}-stimuli_data.json", "w") as output_file:
            json.dump(self.stimuli_data, output_file)
        self.stimuli_data = []

    def save_metadata(self):
        self.metadata["Assay Date"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(f"{self.data_save_location}/{self.assay_configuration_id}.json", "w") as output_file:
            json.dump(self.metadata, output_file)

    def package_output_data(self, observation, rev_observation, action, advantage_stream, rnn_state, rnn2_state, position, prey_consumed, predator_body,
                            conv1l, conv2l, conv3l, conv4l, conv1r, conv2r, conv3r, conv4r,
                            prey_positions, predator_position, sand_grain_positions, vegetation_positions, fish_angle):
        """

        :param action:
        :param advantage_stream:
        :param rnn_state:
        :param position:
        :param prey_consumed:
        :param predator_body: A boolean to say whether consumed this step.
        :param conv1l:
        :param conv2l:
        :param conv3l:
        :param conv4l:
        :param conv1r:
        :param conv2r:
        :param conv3r:
        :param conv4r:
        :param prey_positions:
        :param predator_position:
        :param sand_grain_positions:
        :param vegetation_positions:
        :return:
        """
        # Make output data JSON serializable
        action = int(action)
        advantage_stream = advantage_stream.tolist()
        rnn_state = rnn_state.c.tolist()
        position = list(position)
        # observation = observation.tolist()

        data = {
            "behavioural choice": action,
            "rnn state": rnn_state,
            "rnn 2 state": rnn2_state,
            "advantage stream": advantage_stream,
            "position": position,
            "observation": observation,
            "rev_observation": rev_observation,
            "left_conv_1": conv1l,
            "left_conv_2": conv2l,
            "left_conv_3": conv3l,
            "left_conv_4": conv4l,
            "right_conv_1": conv1r,
            "right_conv_2": conv2r,
            "right_conv_3": conv3r,
            "right_conv_4": conv4r,
            "prey_positions": prey_positions,
            "predator_position": predator_position,
            "sand_grain_positions": sand_grain_positions,
            "vegetation_positions": vegetation_positions,
            "fish_angle": fish_angle,
            "hunger": self.simulation.fish.hungry,
            "stress": self.simulation.fish.stress,
        }

        if prey_consumed:
            data["consumed"] = 1
        else:
            data["consumed"] = 0
        if predator_body is not None:
            data["predator"] = 1
        else:
            data["predator"] = 0

        stimuli = self.simulation.stimuli_information
        to_save = {}
        for stimulus in stimuli.keys():
            if stimuli[stimulus]:
                to_save[stimulus] = stimuli[stimulus]

        if to_save:
            self.stimuli_data.append(to_save)

        return data

    def make_recordings(self, available_data):
        """No longer used - saves data in JSON"""

        step_data = {i: available_data[i] for i in self.assay_output_data_format}
        for d_type in step_data:
            self.assay_output_data[d_type].append(available_data[d_type])
        step_data["step"] = self.step_number
        self.assay_output_data.append(step_data)

    def save_assay_results(self, assay):
        """No longer used - saves data in JSON"""
        # Saves all the information from the assays in JSON format.
        if assay["save frames"]:
            make_gif(self.frame_buffer, f"{self.data_save_location}/{assay['assay id']}.gif",
                     duration=len(self.frame_buffer) * self.learning_params['time_per_step'],
                     true_image=True)

        self.frame_buffer = []
        with open(f"{self.data_save_location}/{assay['assay id']}.json", "w") as output_file:
            json.dump(self.assay_output_data, output_file)
