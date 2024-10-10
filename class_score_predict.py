import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    midterm_range = np.array([0, 125])
    final_range = np.array([0, 100])

    # Load score data
    class_kr = np.loadtxt('data/class_score_kr.csv', delimiter=',')
    class_en = np.loadtxt('data/class_score_en.csv', delimiter=',')
    data = np.vstack((class_kr, class_en))

    # Estimate a line, final = slope * midterm + y_intercept
    midterm_values = data[:, 0]
    final_values = data[:, 1]
    A = np.vstack([midterm_values, np.ones(len(midterm_values))]).T
    A_inv = np.linalg.pinv(A)
    coefficients = A_inv @ final_values
    slope, intercept = coefficients
    line = [slope, intercept]

    # Predict scores
    final = lambda midterm: line[0] * midterm + line[1]
    while True:
        try:
            given = input('Q) Please input your midterm score (Enter or -1: exit)? ')
            if given == '' or float(given) < 0:
                break
            print(f'A) Your final score is expected to {final(float(given)):.3f}.')
        except Exception as ex:
            print(f'Cannot answer the question. (message: {ex})')
            break

    # Plot scores and the estimated line
    plt.figure()
    plt.plot(data[:,0], data[:,1], 'r.', label='The given data')
    plt.plot(midterm_range, final(midterm_range), 'b-', label='Prediction')
    plt.xlabel('Midterm scores')
    plt.ylabel('Final scores')
    plt.xlim(midterm_range)
    plt.ylim(final_range)
    plt.grid()
    plt.legend()
    plt.show()
