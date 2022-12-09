from get_data import GetData

def main():
    gd = GetData()
    # print("petrol")
    # gd.get_prices('petrol')

    # print("diesel")
    # gd.get_current_prices('diesel')
    # gd.get_city_and_id()
    
    # gd.get_last_year_data(2, 'Delhi')
    gd.get_whole_year_prices()

if __name__ == "__main__":
    main()