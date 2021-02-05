import openpyxl as xl

from distributions import Distribution
from insurance import Insurance

"""this dictionary contains the distributions. To add a distribution,
append the table in Excel, the following dictionary and add a new class in 
distributions.py and add a new elif expression in the constructor of the 
Distribution class"""
d = ("B", "NB", "P", "LOG", "GEO")
distr = {}
for i in range(1, 6):
    distr[i] = d[i - 1]



def main():
    """Get information from panjer_recursion.xlsx"""
    wb = xl.load_workbook("panjer_recursion.xlsx")
    ws1 = wb['Main']

    """Number of claims distribution"""
    n_o_c = Distribution(type=distr[ws1['E2'].value], value1=ws1['E3'].value, value2=ws1['E4'].value, trunc=ws1['E6'].value)
    """Amount per claim Distribution"""
    a_p_c = Distribution(type=distr[ws1['F2'].value], value1=ws1['F3'].value, value2=ws1['F4'].value, trunc=ws1['F6'].value)
    """Initialize an instance of the Insurance class """
    Ins = Insurance(n_o_c,a_p_c)

    """amount needed"""
    ruin = Ins.ruin(ws1['I2'].value)

    """scaling factor"""
    sc = ws1['F5'].value

    """Bold Font"""
    b= xl.styles.Font(name='Calibri', size=11, bold=True, color='FF000000')

    ws2 = wb.create_sheet(str(Ins))

    ws2['A1'].value = "n"
    ws2['A1'].font = b
    ws2['A1'].fill = xl.styles.PatternFill("solid", fgColor="009682")

    ws2['B1'].value = "P(S=n)"
    ws2['B1'].font = b
    ws2['B1'].fill = xl.styles.PatternFill("solid", fgColor="009682")

    """write, ruin number expected value and variance"""
    ws2['K1'].value = str(ws1['I2'].value*100)+"% Ruin #"
    ws2['K1'].font = b
    ws2.column_dimensions['K'].width = len(str(ws2['K1'].value))
    ws2['K1'].fill = xl.styles.PatternFill("solid", fgColor="009682")
    ws2['K2'].value = sc * ruin



    ws2['L1'].value = "Mean"
    ws2['L1'].font = b
    ws2['L1'].fill = xl.styles.PatternFill("solid", fgColor="009682")
    ws2['L2'].value = sc*Ins._ex_Value

    ws2['M1'].value = "Variance"
    ws2['M1'].font = b
    ws2['M1'].fill = xl.styles.PatternFill("solid", fgColor="009682")
    ws2['M2'].value = sc**2*Ins._variance

    j=0
    while Ins.cantelli(j)>ws1['I2'].value:
        j += 1

    ws2['N1'].value = "Cantelli"
    ws2['N1'].font = b
    ws2['N1'].fill = xl.styles.PatternFill("solid", fgColor="009682")
    ws2['N2'].value = sc*j

    ws2['O1'].value = "Sc. Factor"
    ws2['O1'].font = b
    ws2['O1'].fill = xl.styles.PatternFill("solid", fgColor="009682")
    ws2['O2'].value = sc

    res = 0
    for i in range(0,ruin+1):
        ws2.cell(column=1, row = i+2, value = sc*i)
        ws2.cell( column = 2, row = i+2,value = Ins.prob_S(i))
        res += Ins.prob_S(i)



    n = xl.chart.Reference(ws2,min_col =1,min_row =2, max_row = ruin+10)
    pn = xl.chart.Reference(ws2,min_col=2,min_row = 1,max_row = ruin+10)

    chart = xl.chart.ScatterChart()
    chart.x_axis.title = 'n'
    chart.y_axis.title = 'P(S=n)'
    series = xl.chart.Series(pn, n, title_from_data=True)

    chart.series.append(series)
    chart.title = "Total Claims Distribution"
    chart.style = 13

    s = chart.series[0]
    s.marker.symbol = "triangle"
    s.marker.graphicalProperties.solidFill = "009682"  # Marker filling
    s.marker.graphicalProperties.line.solidFill = "009682"  # Marker outline
    s.graphicalProperties.line.noFill = True

    ws2.add_chart(chart,'c1')

    wb.save("panjer_recursion.xlsx")




if __name__ == '__main__':
    main()
