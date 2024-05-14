const int emgPin = A0; // Broche analogique pour le capteur EMG
const int sampleInterval = 100; // Intervalle d'échantillonnage en millisecondes (100 ms)
const int numSamples = 50; // Nombre d'échantillons à collecter
int emgValues[numSamples]; // Tableau pour stocker les valeurs EMG

void setup() {
    Serial.begin(9600); // Initialisation de la communication série
}

void loop() {
    static unsigned long startTime = millis(); // Temps de départ
    static int sampleCount = 0; // Compteur d'échantillons

    unsigned long currentTime = millis(); // Temps actuel

    if (currentTime - startTime >= sampleInterval) {
        startTime = currentTime; // Mettre à jour le temps de départ

        // Lire la valeur du capteur EMG
        int emgValue = analogRead(emgPin);

        // Stocker la valeur dans le tableau
        emgValues[sampleCount] = emgValue;

        // Incrémenter le compteur d'échantillons
        sampleCount++;

        // Si nous avons collecté suffisamment d'échantillons, envoyer au Raspberry Pi
        if (sampleCount == numSamples) {
            sendToRaspberryPi(emgValues, numSamples);
            sampleCount = 0; // Réinitialiser le compteur
        }
    }
}

void sendToRaspberryPi(int values[], int numValues) {
    // Ici, vous pouvez implémenter le code pour envoyer les données au Raspberry Pi
    // Par exemple, via une connexion série, Bluetooth ou Wi-Fi
    // Assurez-vous d'adapter cette partie à votre configuration spécifique.
    // Pour l'exemple, nous imprimons simplement les valeurs sur le moniteur série.
    for (int i = 0; i < numValues; i++) {
        /*Serial.print("EMG Value ");
        Serial.print(i + 1);
        Serial.print(": ");*/
        Serial.println(values[i]);
    }
}
