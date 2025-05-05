

class Utils:

    def append_data_rows(cellrange):
        data_rows = []
        for row in cellrange:
            data_cols = []
            for cell in row:
                data_cols.append(cell.value)
            data_rows.append(data_cols)
        
        return data_rows