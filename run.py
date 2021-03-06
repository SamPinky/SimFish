import os
from datetime import datetime
import json

from Services.trial_manager import TrialManager

# Ensure Output File Exists
if not os.path.exists("./Training-Output/"):
    os.makedirs("./Output/")

if not os.path.exists("./Assay-Output/"):
    os.makedirs("./Assay-Output/")


# 4
prey_only_4 = [33, 52, 65, 247, 311, 376, 486]
pred_only_4 = [4, 7, 12, 13, 15, 19, 20, 23, 24, 25, 26, 27, 28, 43, 45, 46, 47, 48, 50, 51, 53, 55, 56, 61, 62, 63, 66, 67, 69, 75, 76, 77, 78, 80, 82, 83, 85, 88, 89, 90, 94, 95, 96, 97, 98, 99, 101, 102, 104, 105, 106, 107, 108, 111, 118, 119, 120, 121, 124, 125, 126, 127, 128, 130, 131, 135, 137, 139, 144, 147, 153, 156, 157, 159, 163, 167, 168, 173, 184, 185, 191, 192, 193, 197, 201, 203, 205, 206, 209, 211, 213, 214, 215, 219, 220, 221, 223, 224, 225, 227, 228, 229, 231, 232, 235, 238, 244, 245, 246, 251, 254, 255, 258, 263, 267, 280, 282, 286, 288, 289, 293, 299, 306, 312, 315, 318, 320, 321, 322, 337, 351, 353, 354, 356, 362, 364, 377, 394, 398, 399, 400, 407, 409, 410, 412, 419, 426, 437, 447, 465, 470, 472, 481, 484, 489, 492, 503]
prey_in_front_4 = [3, 9, 10, 30, 35, 38, 42, 52, 58, 59, 68, 87, 103, 109, 113, 117, 134, 142, 145, 148, 149, 162, 164, 171, 172, 175, 176, 179, 180, 181, 189, 190, 198, 207, 216, 222, 226, 236, 239, 241, 243, 253, 256, 257, 276, 283, 287, 292, 297, 305, 308, 309, 313, 316, 333, 334, 335, 344, 346, 357, 376, 381, 383, 384, 386, 388, 391, 396, 397, 401, 403, 421, 422, 429, 430, 436, 439, 443, 445, 446, 455, 461, 473, 490, 495, 497, 498, 508, 510, 511]

# 5
prey_only_5 = [8, 13, 29, 44, 51, 52, 53, 59, 60, 65, 69, 76, 86, 90, 98, 116, 121, 122, 129, 134, 138, 142, 149, 157, 171, 173, 176, 182, 184, 188, 191, 201, 205, 217, 221, 232, 239, 250, 260, 289, 315, 328, 329, 332, 347, 362, 385, 390, 395, 399, 402, 406, 411, 415, 419, 429, 436, 446, 469, 481, 488, 497, 504]
pred_only_5 = [5, 9, 15, 16, 17, 22, 41, 42, 46, 47, 56, 57, 70, 73, 77, 85, 89, 93, 95, 99, 100, 101, 106, 118, 120, 123, 127, 133, 136, 139, 145, 158, 163, 166, 172, 174, 178, 179, 181, 183, 190, 193, 194, 199, 200, 204, 208, 213, 220, 234, 236, 249, 251, 253, 255, 261, 263, 266, 269, 271, 277, 295, 296, 303, 307, 321, 338, 342, 364, 372, 381, 382, 383, 409, 424, 449, 450, 454, 456, 461, 462, 470, 474, 483, 495, 496, 501, 503, 505, 509, 511]
prey_in_front_5 = [0, 6, 11, 21, 26, 27, 29, 31, 44, 48, 63, 71, 82, 87, 102, 105, 107, 109, 113, 115, 117, 121, 128, 137, 140, 141, 143, 144, 147, 153, 155, 159, 160, 165, 180, 182, 185, 197, 203, 205, 207, 209, 210, 215, 218, 227, 228, 240, 242, 243, 246, 247, 254, 268, 270, 273, 274, 278, 280, 283, 286, 287, 297, 298, 306, 308, 310, 311, 313, 322, 323, 324, 325, 332, 333, 334, 335, 341, 343, 344, 350, 351, 352, 354, 355, 361, 362, 366, 368, 374, 376, 397, 400, 402, 403, 412, 413, 416, 419, 423, 425, 426, 427, 428, 429, 430, 433, 435, 437, 439, 440, 441, 442, 446, 447, 448, 455, 459, 464, 466, 472, 473, 475, 476, 477, 482, 485, 486, 491, 493, 499, 500, 510]

# 6
prey_only_6 = [284, 309, 343, 403, 475, 496, 511]
pred_only_6 = [2, 8, 9, 10, 18, 21, 27, 28, 37, 40, 47, 63, 64, 72, 86, 89, 93, 104, 105, 107, 112, 119, 129, 132, 144, 147, 150, 159, 162, 167, 174, 187, 192, 193, 201, 205, 206, 211, 212, 213, 224, 227, 244, 245, 256, 272, 273, 292, 297, 304, 311, 315, 326, 337, 345, 354, 389, 390, 397, 404, 419, 427, 428, 436, 437, 440, 445, 448, 450, 453, 461, 465, 473, 479, 486, 487, 495, 503, 508]
prey_in_front_6 = [262, 7, 392, 14, 17, 20, 281, 282, 293, 171, 48, 178, 179, 308, 309, 56, 185, 186, 60, 319, 322, 451, 69, 197, 76, 207, 80, 336, 338, 83, 470, 90, 353, 98, 483, 101, 357, 485, 370, 373, 374, 247, 123, 511]

# 7
prey_only_7 = [3, 135, 150, 173, 178, 203, 206, 232, 234, 253, 279, 281, 312, 319, 341, 349, 379, 393, 403, 439, 454, 464, 498]
pred_only_7 = [1, 23, 25, 31, 37, 38, 39, 44, 45, 50, 57, 60, 67, 70, 71, 73, 78, 80, 81, 84, 86, 89, 90, 91, 101, 102, 104, 107, 114, 124, 144, 146, 152, 153, 163, 166, 179, 180, 186, 187, 188, 195, 198, 199, 200, 212, 220, 224, 229, 233, 240, 249, 255, 271, 277, 280, 287, 293, 304, 308, 309, 318, 353, 354, 359, 365, 367, 368, 371, 372, 377, 380, 384, 389, 398, 416, 423, 426, 438, 443, 445, 463, 465, 473, 478, 483, 492, 493, 494, 499, 501, 505, 511]
prey_in_front_7 =[4, 5, 14, 15, 17, 21, 22, 30, 35, 48, 55, 58, 63, 64, 66, 74, 75, 82, 92, 95, 97, 99, 111, 113, 116, 118, 123, 136, 137, 140, 142, 147, 148, 149, 156, 158, 167, 170, 182, 184, 194, 197, 201, 205, 207, 209, 215, 225, 226, 235, 238, 248, 252, 266, 279, 292, 294, 301, 305, 311, 316, 323, 328, 331, 333, 336, 337, 338, 339, 346, 351, 363, 366, 369, 375, 388, 390, 397, 404, 405, 410, 411, 418, 420, 425, 428, 432, 435, 436, 440, 442, 444, 450, 451, 458, 466, 469, 470, 479, 480, 484, 485, 488, 500, 502, 510]


with open(f"Run-Configurations/4-15-Centre_prey_only.json", 'r') as f:
    c1 = json.load(f)

with open(f"Run-Configurations/5-15-Centre_prey_only.json", 'r') as f:
    c2 = json.load(f)

with open(f"Run-Configurations/6-15-Centre_prey_only.json", 'r') as f:
    c3 = json.load(f)

with open(f"Run-Configurations/8-15-Centre_prey_only.json", 'r') as f:
    c4 = json.load(f)


target_ablation = c1 + c2 + c3 + c4

# with open(f"Run-Configurations/differential_prey_low_predator_exploration.json", 'r') as f:
#     missing = json.load(f)
#
# with open(f"Run-Configurations/differential_naturalistic_exploration.json", 'r') as f:
#     c2 = json.load(f)
#
# target_ablation = c1 + c2

with open(f"Run-Configurations/new_ind_ablations_1.json", 'r') as f:
    c1 = json.load(f)

with open(f"Run-Configurations/new_ind_ablations_2.json", 'r') as f:
    c2 = json.load(f)

with open(f"Run-Configurations/even_4_po_prey_only.json", 'r') as f:
    sss = json.load(f)

final_configs = c1 + c2
with open(f"Run-Configurations/vrv_full_config.json", 'r') as f:
    sss = json.load(f)

even_training_configuration = [
    {
        "Model Name": "new_even_prey_ref",
        "Environment Name": "even_prey",
        "Trial Number": 5,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
    {
        "Model Name": "new_even_prey_ref",
        "Environment Name": "even_prey",
        "Trial Number": 6,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
    {
        "Model Name": "new_even_prey_ref",
        "Environment Name": "even_prey",
        "Trial Number": 7,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
    {
        "Model Name": "new_even_prey_ref",
        "Environment Name": "even_prey",
        "Trial Number": 8,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
]

differential_training_configuration = [
    {
        "Model Name": "new_differential_prey_ref",
        "Environment Name": "differential_prey",
        "Trial Number": 3,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
    {
        "Model Name": "new_differential_prey_ref",
        "Environment Name": "differential_prey",
        "Trial Number": 4,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
    {
        "Model Name": "new_differential_prey_ref",
        "Environment Name": "differential_prey",
        "Trial Number": 5,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
    {
        "Model Name": "new_differential_prey_ref",
        "Environment Name": "differential_prey",
        "Trial Number": 6,
        "Total Configurations": 4,
        "Episode Transitions": {
        },
        "Conditional Transitions": {
            "Prey Caught": {
                "2": 5,
                "3": 8,
                "4": 10,
            },
            "Predators Avoided": {
            },
            "Sand Grains Bumped": {
            }
        },
        "Run Mode": "Training",
        "Tethered": False,
        "Realistic Bouts": True,
        "Priority": 2,
        "Using GPU": True,
        "monitor gpu": False,
    },
]

print(f"Start time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
manager = TrialManager(target_ablation)
manager.run_priority_loop()
