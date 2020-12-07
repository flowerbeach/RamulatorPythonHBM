from typing import List, Dict
from configs import strings
from offchip.memory_data_structure import Request


class RowTable(object):
    from offchip.memory_controller import Controller
    from offchip.dram_spec import BaseSpec as t_spec
    
    class Entry(object):
        def __init__(self, row, hits, timestamp):
            self.row = row
            self.hits = hits
            self.timestamp = timestamp
    
    def __init__(self, controller):
        self.ctrl = controller  # type: RowTable.Controller
        self.table = {}  # type: Dict[list, RowTable.Entry]
    
    def update(self, cmd, addr_list, cycle_current):
        row_group = addr_list[:self.t_spec.level.row.value]
        row = addr_list[self.t_spec.level.row.value]
        spec = self.ctrl.channel.spec
        
        if spec.is_opening(cmd) is True:
            self.table[row_group] = RowTable.Entry(row, 0, cycle_current)
        
        if spec.is_accessing(cmd) is True:
            # we are accessing a row -- update its entry
            assert row_group in self.table.keys()
            entry = self.table[row_group]
            assert entry.row == row
            entry.timestamp = cycle_current
            entry.hits += 1
        
        if spec.is_closing(cmd) is True:
            # we are closing one or more rows -- remove their entries
            n_rm = 0
            if spec.is_accessing(cmd) is True:
                scope = self.t_spec.level.row.value - 1
            else:
                scope = spec.scope[cmd.value]
            table_keys = list(self.table.keys())
            for key in table_keys:
                if key[:scope + 1] == addr_list[:scope + 1]:
                    n_rm += 1
                    del self.table[key]
            assert n_rm > 0
            assert n_rm == 1
    
    def get_hits(self, addr_list, to_opened_row=False):
        row_group = addr_list[:self.t_spec.level.row.value]
        row = addr_list[self.t_spec.level.row.value]
        if row_group not in self.table.keys():
            return 0
        elif to_opened_row is False and self.table[row_group].row != row:
            return 0
        return self.table[row_group].hits
    
    def get_open_row(self, addr_list: list):
        row_group = addr_list[:self.t_spec.level.row.value]
        if row_group in self.table.keys():
            return self.table[row_group].row
        else:
            return -1


if __name__ == '__main__':
    a = {'aaa': 1, 3: '5', 55: '3'}
    print(a)
    keys = list(a.keys())
    for k in keys:
        if k == 3:
            del a[k]
    print(a)
