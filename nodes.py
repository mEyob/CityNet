NODES = [
    'W03B', 'W037', 'W00X', 'W00D', 'W00C', 'W00B', 'W00A', 'W009', 'W007',
    'W006', 'W004', 'W002', 'W001', 'W000', 'VN0', 'THS1', 'SPS2', 'SPS1',
    'Ret_waggle_006', 'RET', 'OZO1', 'LNK5', 'IUH0', 'DLW30', 'DLW29', 'DLW28',
    'DLW27', 'DLW26', 'DLW25', 'DLW24', 'DLW23', 'DLW22', 'DLW21', 'DLW20',
    'DLW19', 'DLW18', 'DLW17', 'DLW16', 'DLW15', 'DLW14', 'DLW13', 'DLW12',
    'DLW11', 'DLW10', 'DLW09', 'DLW08', 'DLW07', 'DLW06', 'DLW05', 'DLW04',
    'DLW03', 'DLW02', 'DLW01', 'BRT03', 'AoT_Chicago', '890', '145', '144',
    '143', '142', '141', '140', '13F', '13E', '13D', '13C', '13B', '13A',
    '139', '131', '130', '12F', '12E', '12D', '12C', '12B', '12A', '121',
    '120', '11F', '11E', '11D', '11C', '11B', '11A', '119', '118', '117',
    '116', '115', '114', '113', '112', '111', '110', '10F', '10E', '10D',
    '10C', '10B', '10A', '109', '108', '107', '106', '105', '104', '102',
    '101', '100', '0FF', '0FE', '0FD', '0FC', '0FB', '0FA', '0F9', '0F8',
    '0F7', '0F6', '0F5', '0F4', '0F3', '0F2', '0F1', '0F0', '0EF', '0EE',
    '0ED', '0EC', '0EA', '0E9', '0E8', '0E6', '0E5', '0E1', '0E0', '0DF',
    '0DE', '0DD', '0DC', '0DB', '0DA', '0D9', '0D8', '0D7', '0D6', '0D5',
    '0D4', '0D3', '0D2', '0D1', '0CF', '0CE', '0CD', '0CC', '0CB', '0CA',
    '0C9', '0C8', '0C7', '0C6', '0C4', '0C3', '0C2', '0C1', '0C0', '0BF',
    '0BE', '0BD', '0BB', '0BA', '0B9', '0B8', '0B7', '0B6', '0B5', '0B4',
    '0B3', '0B2', '0B1', '0B0', '0AF', '0AE', '0AD', '0AC', '0AB', '0AA',
    '0A9', '0A7', '0A6', '0A5', '0A4', '0A3', '0A2', '0A1', '0A0', '09F',
    '09D', '09C', '09B', '09A', '099', '098', '097', '096', '095', '094',
    '093', '092', '091A', '090B', '090A', '08F', '08E', '08D', '08C', '08B',
    '089', '088', '087', '086', '085', '083', '082', '081', '080', '07F',
    '07E', '07D', '07C', '07B', '07A', '079', '078', '077', '076', '075',
    '074', '073', '072', '071', '070', '06E', '06D', '06B', '06A', '067',
    '062', '061', '05E', '05D', '05A', '059', '058', '057', '056', '054',
    '053', '052', '051', '050', '04F', '04E', '04D', '04C', '04B', '04A',
    '049', '048', '043', '042', '041', '040', '03F', '03E', '03D', '03C',
    '03B', '03A', '039', '038', '037', '036', '034', '032', '031', '030',
    '02F', '02E', '02D', '02C', '02A', '029', '028', '027', '026', '025',
    '024', '023', '022', '021', '020', '01F', '01D', '01C', '01B', '01A',
    '019', '018', '017', '016', '015', '014', '013', '012', '011', '010',
    '00F', '00E', '00D', '00C', '00B', '00A', '007', '006', '004', '003',
    '000', '0'
]


def create_node_filter():
    node_filter = "&"
    for node in NODES:
        node_filter = node_filter + "node[]=" + node + "&"
    return node_filter
