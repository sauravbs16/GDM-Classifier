import random

def generate_random_value(min_value, max_value):
    if isinstance(min_value, int) and isinstance(max_value, int):
        return random.randint(min_value, max_value)
    return random.uniform(min_value, max_value)

def generate_random_inputs(features):
    random_inputs = {}
    for feature, value_range in features.items():
        min_value, max_value = value_range
        random_value = generate_random_value(min_value, max_value)
        random_inputs[feature] = random_value
    return random_inputs

def main():
    features = {
        'Age': (18, 45),
        'Body Mass Index (BMI)': (15.01, 40.75),
        'Height': (83, 169),
        'Obesity': (0, 1),
        'OGTT 1h': (3.06, 24.98),
        'OGTT 2h': (2.79, 29.87),
        #'Gestational Diabetes': (0, 1),
        'Ethnicity_GBR': (0, 1),
        'Ethnicity_IND': (0, 1),
        'Ethnicity_OTH': (0, 1),
        'Gravida (Is this your first Pregnancy?)': (0, 1)
    }

    random_inputs = generate_random_inputs(features)

    print("Random Inputs:")
    for feature, value in random_inputs.items():
        print(f"{feature}: {value}")

if __name__ == '__main__':
    main()
