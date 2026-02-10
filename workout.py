import json
import math
import argparse


def get_plates(total_weight, bar_weight):
    if total_weight < bar_weight:
        return "Just the bar"

    plates = [45, 35, 25, 10, 5, 2.5]
    plate_count = {}
    side_weight = (total_weight - bar_weight) / 2

    for plate in plates:
        count = math.floor(side_weight / plate)
        if count > 0:
            plate_count[plate] = count
        side_weight = side_weight % plate

    if not plate_count:
        return "No plates needed"

    return ", ".join(f"{plate}x{count}" for plate, count in plate_count.items())


def get_dumbbells(total_weight):
    each_side = total_weight / 2
    return 2.5 * round(each_side / 2.5)


def snake_to_caps(str):
    return str.replace("_", " ").title()


def create_routine(routine_cfg, weights_cfg, deload=False):
    sets_mult = 1
    weight_mult = 1
    if deload:
        weight_mult = 0.6
        sets_mult = 0.5

    steps = []
    for day in ["day_1", "day_2", "day_3", "day_4"]:
        steps.append(f"# {snake_to_caps(day)}")
        daily_cfg = routine_cfg[day]

        for workout in daily_cfg["order"]:
            steps.append(f"\n### {snake_to_caps(workout)}")
            workout_cfg = daily_cfg[workout]
            working_sets_cfg = workout_cfg["working_sets"]
            sets = math.ceil(working_sets_cfg["sets"] * sets_mult)
            reps = working_sets_cfg["reps"]

            match workout_cfg["type"]:
                # Barbell workouts
                case "barbell_standard" | "barbell_ez_curl" | "trap_bar":
                    bar_types = {
                        "barbell_standard": "Standard Barbell",
                        "barbell_ez_curl": "EZ Curl Barbell",
                        "trap_bar": "Trap Bar",
                    }
                    steps.append(f"*{bar_types[workout_cfg["type"]]}*")

                    workout_weight = (
                        weights_cfg["exercises"][day][workout] * weight_mult
                    )

                    bar_weight = weights_cfg["barbells"][workout_cfg["type"]]

                    if workout_cfg.get("warmup", None):
                        steps.append("Warmup:")

                        for warmup_step in workout_cfg["warmup"]:
                            warmup_weight = warmup_step["ratio"] * workout_weight
                            steps.append(
                                f"- [ ] {warmup_step['reps']} reps of ~{warmup_weight} lbs ({get_plates(warmup_weight, bar_weight)})"
                            )

                    steps.append(
                        f"\nWorking Sets: {sets} sets of {reps} at {workout_weight} lbs ({get_plates(workout_weight, bar_weight)})"
                    )
                    for i in range(sets):
                        steps.append(f"- [ ] Set {i+1}")

                # Dumbbell workouts
                case "dumbbell":
                    workout_weight = (
                        weights_cfg["exercises"][day][workout] * weight_mult
                    )

                    steps.append("*Dumbbell*")

                    steps.append("Warmup:")

                    for warmup_step in workout_cfg["warmup"]:
                        warmup_weight = get_dumbbells(
                            warmup_step["ratio"] * workout_weight
                        )
                        steps.append(
                            f"- [ ] {warmup_step['reps']} reps of ~{warmup_weight} lbs each dumbbell"
                        )
                    steps.append(
                        f"\nWorking Sets: {sets} sets of {reps} at {get_dumbbells(workout_weight)} lbs each dumbbell"
                    )
                    for i in range(sets):
                        steps.append(f"- [ ] Set {i+1}")

                case "body":
                    steps.append("*Body Weight*")
                    steps.append("Warmup: None")
                    steps.append(f"\nWorking Sets: {sets} sets of {reps}")
                    for i in range(sets):
                        steps.append(f"- [ ] Set {i+1}")

            steps.append(f"Rest {workout_cfg['rest']} between each set")
        steps.append("\n")

    return steps


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deload", action="store_true", help="Use deload routine")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    deload = args.deload
    with (
        open("./routine.json") as routine_cfg_file,
        open("./weights.json") as weights_cfg_file,
    ):
        routine_cfg = json.load(routine_cfg_file)
        weights_cfg = json.load(weights_cfg_file)

        steps = create_routine(routine_cfg, weights_cfg, deload)
        with open("./routine.md", "w") as routine_file:
            routine_file.write("\n".join(steps))
