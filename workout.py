import json
import math


def get_plates(total_weight, bar_weight):
    if total_weight < bar_weight:
        return f"Total weight ({total_weight} lbs) is less than bar weight ({bar_weight} lbs)"

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

    plates_str = ", ".join(f"{plate}x{count}" for plate, count in plate_count.items())
    leftover_str = f", {side_weight:.1f} lbs leftover" if side_weight > 0.01 else ""

    return f"{plates_str}"


def get_dumbbells(total_weight):
    each_side = total_weight / 2
    return 5 * round(each_side / 5)


def snake_to_caps(str):
    return str.replace("_", " ").title()


def create_routine(routine_cfg, weights_cfg):
    steps = []
    for day in ["day_1", "day_2", "day_3", "day_4"]:
        steps.append(snake_to_caps(day))
        daily_cfg = routine_cfg[day]

        for workout in daily_cfg["order"]:
            steps.append(f"\n## {snake_to_caps(workout)}")
            workout_cfg = daily_cfg[workout]
            working_sets_cfg = workout_cfg["working_sets"]

            match workout_cfg["type"]:
                # Barbell workouts
                case "barbell_standard" | "barbell_ez_curl":
                    steps.append(
                        "\tStandard Barbell"
                        if workout_cfg["type"] == "barbell_standard"
                        else "\tEZ Curl Barbell"
                    )
                    workout_weight = weights_cfg["exercises"][day][workout]
                    bar_weight = weights_cfg["barbells"][workout_cfg["type"]]

                    steps.append("\n\tWarmup:")

                    for warmup_step in workout_cfg["warmup"]:
                        warmup_weight = warmup_step["ratio"] * workout_weight
                        steps.append(
                            f"\t\t- {warmup_step['reps']} reps of ~{warmup_weight} lbs ({get_plates(warmup_weight, bar_weight)})"
                        )

                    steps.append("\n\tWorking Sets:")
                    steps.append(
                        f"\t\t- {working_sets_cfg['sets']} sets of {working_sets_cfg["reps"]} at {workout_weight} lbs ({get_plates(workout_weight, bar_weight)})"
                    )

                # Dumbbell workouts
                case "dumbbell":
                    workout_weight = weights_cfg["exercises"][day][workout]

                    steps.append("\n\tWarmup:")

                    for warmup_step in workout_cfg["warmup"]:
                        warmup_weight = get_dumbbells(
                            warmup_step["ratio"] * workout_weight
                        )
                        steps.append(
                            f"\t\t- {warmup_step['reps']} reps of ~{warmup_weight} lbs each dumbbell"
                        )
                    steps.append("\n\tWorking Sets:")
                    steps.append(
                        f"\t\t- {working_sets_cfg['sets']} sets of {working_sets_cfg["reps"]} at {get_dumbbells(workout_weight)} lbs each dumbbell"
                    )

                case "body":
                    steps.append("\n\tWarmup: None")
                    steps.append("\n\tWorking Sets:")
                    steps.append(
                        f"\t\t- {working_sets_cfg['sets']} sets of {working_sets_cfg["reps"]}"
                    )

            steps.append(f"\tRest {workout_cfg['rest']} between each set")
        steps.append("\n")

    return steps


if __name__ == "__main__":
    with (
        open("./routine.json") as routine_cfg_file,
        open("./weights.json") as weights_cfg_file,
    ):
        routine_cfg = json.load(routine_cfg_file)
        weights_cfg = json.load(weights_cfg_file)

        steps = create_routine(routine_cfg, weights_cfg)
        with open("./routine.txt", "w") as routine_file:
            routine_file.write("\n".join(steps))
