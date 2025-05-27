import numpy as np
import tensorflow as tf
import pyttsx3
import matplotlib.pyplot as plt
# Training data
X_train = np.array([
    [1, 1, 0, 1, 0, 0], # Flu
    [0, 1, 1, 0, 0, 0], # Cold
    [1, 1, 0, 0, 1, 0], # COVID-19
    [0, 0, 1, 0, 0, 1] # Allergy
], dtype=np.float32)


y_train = tf.keras.utils.to_categorical([0, 1, 2, 3], num_classes=4)
diseases = ["Flu", "Cold", "COVID-19", "Allergy"]


def build_model():
    inputs = tf.keras.Input(shape=(6,))
    x = tf.keras.layers.Dense(16, activation='relu')(inputs)
    x = tf.keras.layers.Dropout(0.5)(x, training=True)
    x = tf.keras.layers.Dense(16, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x, training=True)
    outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
    return tf.keras.Model(inputs, outputs)


model = build_model()
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=100, verbose=0)


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def predict_with_uncertainty(model, x, n_iter=100):
    preds = np.array([model(x, training=True).numpy() for _ in range(n_iter)])
    mean = preds.mean(axis=0)
    std = preds.std(axis=0)
    return mean, std


def run_virtual_robot():
    print(" Hello! I am your virtual health assistant robot.")
    print("Please answer the following questions with Y/N:")
    symptom_names = ["Fever", "Cough", "Sneezing", "Fatigue", "Loss of Taste", "Itchy Eyes"]
    input_symptoms = []
    for name in symptom_names:
        ans = input(f"Do you have {name}? (Y/N): ").strip().lower()
    input_symptoms.append(1 if ans == 'y' else 0)
    input_array = np.array([input_symptoms], dtype=np.float32)
    mean_probs, std_probs = predict_with_uncertainty(model, input_array)
    most_likely = np.argmax(mean_probs)
    diagnosis = diseases[most_likely]
    print("\n Diagnosis with Probabilities and Uncertainty:")
    for i, dis in enumerate(diseases):
        print(f"{dis}: P={mean_probs[0][i]:.3f}, Uncertainty={std_probs[0][i]:.3f}")
    speak(f"You may have {diagnosis}.")
    print(f"\n Diagnosis: {diagnosis} (±{std_probs[0][most_likely]:.3f})")
    test_map = {
        "Flu": "Influenza A/B test",
        "Cold": "Nasal swab",
        "COVID-19": "PCR test",
        "Allergy": "Allergy skin test"
    }
    medicine_map = {
        "Flu": "Oseltamivir (Tamiflu)",
        "Cold": "Rest, fluids, antihistamines",
        "COVID-19": "Isolation + Paracetamol",
        "Allergy": "Loratadine or Cetirizine"
    }
    speak(
        f"I recommend you take a {test_map[diagnosis]} and consider taking {medicine_map[diagnosis]}"
    )
    print(f"Test: {test_map[diagnosis]}")
    print(f"Medicine: {medicine_map[diagnosis]}")

    print(f" Test: {test_map[diagnosis]}")
    print(f" Medicine: {medicine_map[diagnosis]}")
    plt.bar(diseases, mean_probs[0], yerr=std_probs[0], capsize=5, color='skyblue')
    plt.ylabel("Probability")
    plt.title("Diagnosis Confidence")
    plt.show()
    run_virtual_robot()