from DummyData import run_walk

from Models import lstm_nn
from Models import basic_nn

from Models.save_and_load import save_model
from Models.save_and_load import load_model

from sklearn.metrics import confusion_matrix, classification_report

def evaluate_model(model, get_predictions, test_x, test_y):
    predictions = get_predictions(model, test_x)
    print(confusion_matrix(test_y, predictions))
    print(classification_report(test_y, predictions))

def train_lstm(filename):
    train_data, test_data = run_walk.load_data()

    train_x = train_data.drop('Target Class', axis=1)
    train_y = train_data['Target Class']
    test_x = test_data.drop('Target Class', axis=1)
    test_y = test_data['Target Class']

    timestep = 4
    num_epochs = 5
    model = lstm_nn.get_trained_lstm_model(train_x, train_y, timestep, num_epochs)
    save_model(model, filename)
    test_x, test_y = lstm_nn.encode_data(test_x, test_y, 4)
    evaluate_model(model, lstm_nn.get_predictions, test_x, test_y)

if __name__ == "__main__":
    train_lstm('presentation')
    
    pass
