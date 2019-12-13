fastSimReplacements = [
    ['met_pt','GenMET_pt'],
    ['MET_significance','GenMET_significance'],
    ['met_phi','GenMET_phi'],
    ['dl_mt2ll','dl_mt2ll_gen'],
    ['dl_mt2bb','dl_mt2bb_gen'],
    ['dl_mt2blbl','dl_mt2blbl_gen'],
]
def fastSimGenMetReplacements( cutString ):
    res = cutString
    for r in fastSimReplacements:
        res = res.replace( *r )
    return res
