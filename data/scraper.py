from boeien import ijmuiden, K13, boeien

time_48h48h = "-48,48"
time_48h0h = "-48,0"
time_28d = "-672,0"

if __name__ == '__main__':
    for boei in boeien:
        boei.scrape(time_str=time_28d)
        print(boei.data)
