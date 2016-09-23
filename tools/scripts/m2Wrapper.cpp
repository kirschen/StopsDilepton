/*-------------------------------------------+
|   Main event-interface skeleton code       |
|      for OPTIMASS model classes            |
+--------------------+-----------------------+
          < Model information >
+--------------------------------------------+
#1) Model Name : 'TTbar_AB'
+--------------------------------------------+
#2) Full Decay Topology :
+--------------------------------------------+
    chain-(1) : ab - t1 t2 , ( t1 - b1 w1 , w1 - e1 v1 ) , ( t2 - b2 w2 , w2 - e2 v2 )
+--------------------------------------------+
#3) Full Invisible Leaf Particles :
+--------------------------------------------+
    ['v1', 'v2']
+--------------------------------------------+
#4) Target Mother Particles :
+--------------------------------------------+
    ['t1', 't2']
+--------------------------------------------+
#5) Effective Invisible Particles :
+--------------------------------------------+
    ['v1', 'v2']
+--------------------------------------------+
#6) Constraint Function List :
+--------------------------------------------+
    constraint-(1) : t1.M() - t2.M() = 0 
    constraint-(2) : w1.M() - w2.M() = 0
+--------------------------------------------*/
#include <cmath>
#include <string>
#include <iostream>
#include "TH1.h"
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TCanvas.h"
#include "TClonesArray.h"
#include "TLorentzVector.h"

#include "MassMinimizer.h"
#include "ProcessTree.h"
#include "ALMController.h"

#include "TTbar_AB.h"

using namespace std;

class m2Wrapper {

    public:

    bool verbose = false;

    // Enumerate M2 variants. For now, have only M2CC.
    enum M2Variant {M2CC=0};

    double calcM2(TLorentzVector lepton1, TLorentzVector lepton2, TLorentzVector bquark1, TLorentzVector bquark2, TVector2 ETmiss, M2Variant variant = M2CC) {

        OptiMass::MassMinimizer *optm = 0;
        optm = static_cast<OptiMass::MassMinimizer *>(new OptiMass::TTbar_AB);
        optm->InitContainers();

        OptiMass::ProcessTree   & process_tree   = optm->GetProcessTree();
        OptiMass::ALMController & alm_controller = optm->GetALMController();

        optm->SetInvisibleSubsystemMomenta(0,
            ETmiss.Px(),
            ETmiss.Py()
        );

        // Visible Momentum Input :
        optm->SetMomentumValue("b1_x",bquark1.Px());
        optm->SetMomentumValue("b1_y",bquark1.Py());
        optm->SetMomentumValue("b1_z",bquark1.Pz());
        optm->SetMomentumValue("b1_m",bquark1.M() );
        optm->SetMomentumValue("e1_x",lepton1.Px());
        optm->SetMomentumValue("e1_y",lepton1.Py());
        optm->SetMomentumValue("e1_z",lepton1.Pz());
        optm->SetMomentumValue("e1_m",lepton1.M() );
        optm->SetMomentumValue("b2_x",bquark2.Px());
        optm->SetMomentumValue("b2_y",bquark2.Py());
        optm->SetMomentumValue("b2_z",bquark2.Pz());
        optm->SetMomentumValue("b2_m",bquark2.M() );
        optm->SetMomentumValue("e2_x",lepton2.Px());
        optm->SetMomentumValue("e2_y",lepton2.Py());
        optm->SetMomentumValue("e2_z",lepton2.Pz());
        optm->SetMomentumValue("e2_m",lepton2.M());

        // Invisible Particle (Trial) Mass Input :
        optm->SetInitInvisibleMomentum("v1_m", 0. );
        optm->SetInitInvisibleMomentum("v2_m", 0. );    

        if (variant == M2CC) {
                //for M2CC
                optm->UseConstraint(0, true);// (true or false) for the constraint : t1.M() - t2.M() = 0.
                optm->UseConstraint(1, true);// (true or false) for the constraint : w1.M() - w2.M() = 0.
        } else {
                cout<<" Do nothing for variant "<<variant<<endl;
        }
 
       /*-----------------------+
        | OptiMass Calculation  |
        +-----------------------*/
        optm->Calc();

        //---------------------------------------+
        //  Print output of the current result   |
        //---------------------------------------+
        if ( verbose ) {
            cout << "==================================================" << endl;
            //cout << "Event ID    = "<< entry << endl;
            cout << "OptiMass    = "<< sqrt(optm->GetOptiMass()) << endl; 
            cout << "==================================================" << endl;
            cout << "<Reconstructed Particle Masses in full decay system> " << endl;
            cout << "ab-mass = " << process_tree.GetSubsystemMass("ab") << endl;
            cout << "t1-mass = " << process_tree.GetSubsystemMass("t1") << endl;
            cout << "w1-mass = " << process_tree.GetSubsystemMass("w1") << endl;
            cout << "v1-mass = " << process_tree.GetSubsystemMass("v1") << endl;
            cout << "t2-mass = " << process_tree.GetSubsystemMass("t2") << endl;
            cout << "w2-mass = " << process_tree.GetSubsystemMass("w2") << endl;
            cout << "v2-mass = " << process_tree.GetSubsystemMass("v2") << endl;
            cout << "==================================================" << endl;
            cout << "modConst    = "<< alm_controller.GetSumSquaredConstraints() << endl; // norm of the constraint functions (turned-on)
            cout << "nIter       = "<< alm_controller.GetNumberIteration() << endl;
            cout << "nALM-Phase1 = "<< alm_controller.GetNumberPhase1() << endl;
            cout << "nALM-Phase2 = "<< alm_controller.GetNumberPhase2() << endl;
            cout << "==================================================" << endl;
        }

        double result = sqrt( optm->GetOptiMass() );
        
        delete optm;

        return result;
 
    }; 
 
};
