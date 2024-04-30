import pandas as pd
import pickle

test_data = pd.read_csv("./input_data/output.csv", encoding='latin1', usecols=lambda column: column != 'URL')
url = pd.read_csv("./input_data/output.csv", encoding='latin1', usecols=lambda column: column == 'URL')

with open('XGBoost_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

predicted_results = loaded_model.predict(test_data)

predicted = pd.DataFrame({'URL': url['URL'], 'Predicted_result': predicted_results})

predicted.to_csv('predicted_result.csv', index=False)

with open('predicted_result.csv', 'r') as f_in:
    with open('predicted_result.txt', 'w') as f_out:
        for line in f_in:
            f_out.write(line)
