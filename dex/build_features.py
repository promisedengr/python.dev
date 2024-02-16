# load data libraries
import pandas as pd
import numpy as np


def summarize_daily(df, cols, irr_filter=100):
    """
    Summarize dataframe based on expected available columns

    :param df: Dataframe
    :param cols: List of columns and summary aggregation type
                    ex. {'PmaxTcorr': 'mean'}
    """
    df.set_index('ReadTime', inplace=True)

    # filter low irradiance and group to daily
    df_daily = df[(df['Irradiance'] >= irr_filter)].groupby(
        ['StartDate', 'Sequence', 'SampleDescription', 'ParentSiteID', 'SiteName', 'DASName', 'InvestigationId',
         'EquipmentName', 'TableRank', 'StringID', 'MPPT', 'nModules']).resample('1D').agg(cols).reset_index()

    df.reset_index(inplace=True)
    # move column ReadTime to beginning
    df_daily.insert(0, 'ReadTime', df_daily.pop('ReadTime'))

    return df_daily


def add_pmax_stc(df):
    """
    Add a new calculated Pmax_STC column to the dataframe

    :param df: Dataframe
    """
    df['Pmax_STC'] = (df['Pmax'] * (1000 / df['Irradiance'])) / (
            1 + (df['Tco_Pmax'] * (df['TemperatureJunction'] - 25)))

    return df


def add_pmaxtcorr(df):
    """
    Add a new calculated PmaxTcorr column to the dataframe

    :param df: Dataframe
    """
    df['PmaxTcorr'] = (df['Pmax']) / (1 + (df['Tco_Pmax'] * (df['TemperatureJunction'] - 25)))

    return df


def ppi_calc(df, df_daily):
    """
    Perform linear regression on df PmaxTcorr vs Irradiance and calculate PPI to the df_daily dataframe

    :param df: 15-minute dataframe for linear fit
    :param df_daily: daily dataframe for PPI column
    """
    # Table cleanup
    df_daily.drop_duplicates(inplace=True)

    # create table subset and remove NaN rows that would prevent PPI calculation
    df_temp = df[(df['Irradiance'] >= 600) & (df['Irradiance'] <= 1100)]
    df_temp = df_temp.dropna(how='any', subset=['Irradiance', 'PmaxTcorr', 'Pmax_AH'])

    # Create PPI column
    df_daily['PPI'] = ''

    for i in range(len(df_daily)):
        try:
            ppi_calc = df_temp[(df_temp.ReadTime.dt.date == df_daily.ReadTime.dt.date.iloc[i]) &
                               (df_temp.SiteName == df_daily.SiteName.iloc[i]) &
                               (df_temp.Sequence == df_daily.Sequence.iloc[i]) &
                               (df_temp.SampleDescription == df_daily.SampleDescription.iloc[i]) &
                               (df_temp.EquipmentName == df_daily.EquipmentName.iloc[i]) &
                               (df_temp.TableRank == df_daily.TableRank.iloc[i]) &
                               (df_temp.StringID == df_daily.StringID.iloc[i]) &
                               (df_temp.MPPT == df_daily.MPPT.iloc[i])][['Irradiance', 'PmaxTcorr', 'Pmax_AH']]
            m, b = np.polyfit(ppi_calc.Irradiance, ppi_calc.PmaxTcorr, deg=1)
            PPI = (m * 1000 + b) / ppi_calc.Pmax_AH.iloc[0]
            df_daily.iloc[i, df_daily.columns.get_loc('PPI')] = PPI
        except Exception as e:
            df_daily.iloc[i, df_daily.columns.get_loc('PPI')] = np.nan
            continue

    return df_daily


def outlier_removal(df, column, column_group):
    """
    Remove Top / Bottom 15% then calculate mean and standard deviation for outlier filtering

    :param df: dataframe
    :param column: column(s) to be evaluated
    :param column_group: column(s) to group by
    """
    # group for column_group
    df_groups = df.groupby(column_group[1:])

    for SiteName, Sample, Sequence, nModules in df_groups.groups:
        df_temp = df[(df['SiteName'] == SiteName) & (df['SampleDescription'] == Sample) & (df['Sequence'] == Sequence)
                     & (df['nModules'] == nModules)]

        # Standard Deviation Calculations to identify outliers
        quantile_15, quantile_85 = df_temp[column].quantile(q=[0.15, 0.85])
        df_temp['P60'] = np.where((quantile_15 < df_temp[column])
                                  & (df_temp[column] < quantile_85), True, False)
        Median = df_temp[[column]].where(df_temp['P60']).median(skipna=True)[0]
        Std_Dev = df_temp[[column]].where(df_temp['P60']).std(skipna=True)[0]
        df_temp['Outlier'] = np.where((Median + (2 * Std_Dev) < df_temp[column])
                                      | (df_temp[column] < Median - (2 * Std_Dev)), True, False)

        # Merge back to original Dataframe
        df.loc[(df['SiteName'] == SiteName) & (df['SampleDescription'] == Sample) & (df['Sequence'] == Sequence)
               & (df['nModules'] == nModules), ['Outlier']] = df_temp['Outlier']

    return df


def calc_energy(df, timeinterval_min=15):
    """
    Add a new calculated Energy column to the dataframe

    param df: Dataframe
    param timeinterval_min: Time interval between measurements in datatable, Default 15 minutes
    """
    df['Energy'] = df['nModules'] * 0.001 * df['Pmax'] * timeinterval_min / 60

    return df


def calc_predictedenergy(df, timeinterval_min=15):
    """
    Add a new calculated Predicted Energy column to the dataframe

    param df: Dataframe
    param timeinterval_min: Time interval between measurements in datatable, Default 15 minutes
    """
    df['PredictedEnergy_kWh'] = df['nModules'] * 0.001 * df['PredictedPower_Watts'] * timeinterval_min / 60

    return df


def calc_actvsexp(df):
    """
    Add a new calculated ActvsExp column to the dataframe

    param df: Dataframe
    """
    df['ActvsExp'] = df['Energy']/df['PredictedEnergy_kWh'] - 1

    return df


if __name__ == '__main__':
    from src.visualization import visualize
