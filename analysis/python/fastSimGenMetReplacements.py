fastSimReplacements = [
    ['met_pt','met_genPt'],
    ['metSig','met_genPt/sqrt(ht)'],
    ['met_phi','met_genPhi'],
    ['dl_mt2ll','dl_mt2ll_gen'],
    ['dl_mt2bb','dl_mt2bb_gen'],
    ['dl_mt2blbl','dl_mt2blbl_gen'],
]
def fastSimGenMetReplacements( cutString ):
    res = cutString
    for r in fastSimReplacements:
        res = res.replace( *r )
    return res
