#ifndef STOPSDILEPTON_TOOLS_PLUGINS_LHEHELPER
#define STOPSDILEPTON_TOOLS_PLUGINS_LHEHELPER

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/FWLite/interface/Handle.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ServiceRegistry/interface/Service.h"


#include "TNtuple.h"
#include "TTree.h"
#include <vector>
#include <typeinfo>
#include <string>


class LHEHelper : public edm::EDAnalyzer
{
public:

  explicit LHEHelper ( const edm::ParameterSet & );
  ~LHEHelper();

  void beginJob(  );
//  void beginRun ( edm::Run & iRun, edm::EventSetup const& iSetup );
  void beginRun( const edm::Run&, const edm::EventSetup& );
//  virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
  void endJob();

//  void analyze ( edm::Event &, const edm::EventSetup &  );


//  private:
//  edm::ParameterSet params_;
//  bool verbose_;

};

#endif
