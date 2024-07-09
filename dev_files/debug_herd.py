from simoolator.herd import Herd
from simoolator.cow import Cow

def model1(weight, height, age):
    bmi = weight / (height ** 2)
    adjusted_bmi = bmi * age
    return adjusted_bmi


def model2(energy_intake, activity_level, weight, height):
    bmr = 10 * weight + 6.25 * height - 5 * 30
    tdee = bmr * activity_level
    caloric_balance = energy_intake - tdee
    return [bmr, tdee, caloric_balance]


def model3(protein_intake, carb_intake, fat_intake, weight):
    total_calories = (protein_intake * 4) + (carb_intake * 4) + (fat_intake * 9)
    calories_per_kg = total_calories / weight
    return {'total_calories': total_calories, 'calories_per_kg': calories_per_kg}


def main():
    herd = Herd(name="Debug Herd")
    herd.load_cows_from_json("./dev_files/demo_cows.json")

    herd.register_model(model1)
    herd.register_model(model2)
    herd.register_model(model3)

    herd.execute_model("model1", execution_mode='linear')
        

if __name__ == "__main__":
    main()
