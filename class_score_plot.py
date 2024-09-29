import matplotlib.pyplot as plt

def read_data(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            if not line.startswith('#'): # If 'line' is not a header
                data.append([int(word) for word in line.split(',')])
    return data

if __name__ == '__main__':
    # Load score data
    class_kr = read_data('data/class_score_kr.csv')
    class_en = read_data('data/class_score_en.csv')

    midterm_kr, final_kr = zip(*class_kr)
    total_kr = [40/125*midterm + 60/100*final for (midterm, final) in class_kr]
    midterm_en, final_en = zip(*class_en)
    total_en = [40/125*midterm + 60/100*final for (midterm, final) in class_en]
    
    plt.figure(figsize=(8, 6))
    xs_kr = [midterm for midterm in midterm_kr]
    ys_kr = [final for final in final_kr]
    xs_en = [midterm for midterm in midterm_en]
    ys_en = [final for final in final_en]
    plt.scatter(xs_kr, ys_kr, color = 'red', label='Korean')
    plt.scatter(xs_en, ys_en, color = 'blue', label = "English", marker='+')
    plt.xlim(0, 125)
    plt.ylim(0, 100)
    plt.xlabel('Midterm scores')
    plt.ylabel('Final scores')
    plt.legend()
    plt.grid()
    plt.savefig('class_score_scatter.png', format='png', dpi=300)
    plt.show()
  
    plt.figure(figsize=(8, 6))
    bins = [i for i in range(0, 101, 5)]
    plt.xticks(range(0, 101, 20))
    plt.xlim(0, 100)
    plt.hist(total_en, bins=bins, color='blue', alpha=0.7, label = "English")
    plt.hist(total_kr, bins=bins, color='red', alpha=0.7, label = "Korean")
    plt.xlabel('Total scores')
    plt.ylabel('The number of students')
    plt.legend()
    plt.savefig('class_score_hist.png', format='png', dpi=300)
    plt.show()