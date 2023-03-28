def get_all_components(funds):
    # creating fund naming components cols in csv
    labels = ["STRATEGY", "SECTOR", "REGION", "VINTAGE", "CLASS", "SERIES", "LEGAL STRUCTURE", "region_acr",
              "sector_acr", "strategy_acr", "ls_acr", "org_ls"]
    funds = get_fund_family(funds, 'FILTERED FUND NAMES')
    funds["Fund Structure"] = funds['FILTERED FUND NAMES'].apply(
        lambda x: get_ls_sector_region_strategy_vintage_series_class(x))
    funds[labels] = pd.DataFrame(funds["Fund Structure"].tolist(), index=funds.index)
    del funds["Fund Structure"]
    return funds
    
    
    
def generate_tickers(funds, user_email=None, file_id=None):
    acronyms = []
    conflict_acronyms = []
    count = 0
    for index, row in funds.iterrows():
        count = count + 1
        try:
            my_acronym = generate_single_ticker(row)
            ticker_obj, ticker_conflict_obj = save_ticker(row, my_acronym[:14], user_email, file_id)
            if ticker_obj:
                acronyms.append(ticker_obj)
            elif ticker_conflict_obj:
                conflict_acronyms.append(ticker_conflict_obj)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Exception in generate_tickers : ", e)
    print("Count :=:", count)
    return acronyms, conflict_acronyms


@print_durations
@transaction.atomic
def save_ticker(item, ticker, user_email, file_id):
    row = insert_components_to_db(item)
    row['ticker'] = ticker.lower()
    ticker_obj = None
    ticker_obj_conflict = None
    try:
        try:
            retired_ticker_obj = RetiredFundTicker.objects.get(ticker=row['ticker'])
            conf_row = copy.copy(row)
            conf_row['reason'] = 'retired'
            ticker_obj_conflict, status = FundTickerConflict.objects.get_or_create(**conf_row)
        except Exception as e:
            ticker_obj, status = FundTicker.objects.get_or_create(**row)

    except IntegrityError as e:
        conf_obj = FundTicker.objects.get(ticker=row['ticker'])
        conf_row = copy.copy(row)
        conf_row['conflicting_ticker'] = conf_obj
        ticker_obj_conflict, status = FundTickerConflict.objects.get_or_create(**conf_row)
    except Exception as e:
        pass
        print("Exception======", e)
    if file_id and ticker_obj:
        file_id.ticker.add(ticker_obj)
    elif file_id and ticker_obj_conflict:
        file_id.conflict_ticker.add(ticker_obj_conflict)

    email_obj = None
    if user_email and ticker_obj:
        email_obj, email_new = UserEmail.objects.get_or_create(email=user_email)
        email_obj.visitor_fund_name.add(row['filtered_fund_name'])
        email_obj.ticker.add(ticker_obj)
    elif user_email and ticker_obj_conflict:
        email_obj, status = UserEmail.objects.get_or_create(email=user_email)
        email_obj.visitor_fund_name.add(row['filtered_fund_name'])
        email_obj.conflict_ticker.add(ticker_obj_conflict)

    fund_name = item.get('FUND NAME', '')
    ffn_obj = row['filtered_fund_name']


    fn_obj = fetch_fund_name(FundName, 'email', email_obj, 'file_id', file_id, 'filtered_fund_name', ffn_obj,
                             'fund_name', fund_name)

    return ticker_obj, ticker_obj_conflict

