
from matplotlib import pyplot as plt
from spots import ijmuiden

if __name__ == '__main__':
    data = ijmuiden.plot_surf_rating()
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)

    plt.savefig("web/forecast-ijmuiden.png")
    plt.show()