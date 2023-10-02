
from matplotlib import pyplot as plt
from spots import ijmuiden, spots, camperduin

if __name__ == '__main__':
    for spot in spots:
        data = spot.plot_surf_rating()
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        plt.savefig(f"web/{spot.name}.png")
        # plt.show()