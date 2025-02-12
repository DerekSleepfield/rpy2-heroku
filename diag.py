import falcon
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
import sys

# import R's utility package
utils = rpackages.importr('utils')

# select a mirror for R packages
utils.chooseCRANmirror(ind=1) # select the first mirror in the list

# Finally, import BlockTools
bt = rpackages.importr('blockTools')

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class DiagResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        
        # capture each of the blocking vars
        cap_partyid = req.params["party.id"]
        cap_linkedfate = req.params["lat.linkedfate"]
        cap_id = req.params["id"]
        py_session = req.params["session"] + ".RData"
        
        py_exact_var = ["party.id", "lat.linkedfate"]
        py_exact_val = [cap_partyid, cap_linkedfate]
        
        if (len(req.params["party.id"]) == 2):
            robjects.r('''
                           f <- function(id, exact_var, exact_val, session) {
                            
                            # the session has not been seen before, then the corresponding file doesn't exist
                            # and this must be the first assignment
                            if(!file.exists(session)) {
                                seqout <- seqblock(query = FALSE
                                                , id.vars = "ID"
                                                , id.vals = id
                                                , n.tr = 6
                                                , tr.names = c(
                                                 "idp",
                                                 "idp+ec",
                                                 "idm",
                                                 "irp",
                                                 "irp+ec",
                                                 "irm")
                                                , assg.prob = c(
                                                .15,
                                                .15,
                                                .2,
                                                .15,
                                                .15,
                                                .2)
                                                , exact.vars = exact_var
                                                , exact.vals = exact_val
                                                , file.name = session)
                            }
                            else {
                                seqout <- seqblock(query = FALSE
                                                , object = session
                                                , id.vals = id
                                                , n.tr = 10
                                                , tr.names = c(
                                                 "idp",
                                                 "idp+ec",
                                                 "idm",
                                                 "irp",
                                                 "irp+ec",
                                                 "irm")
                                                , assg.prob = c(
                                                .15,
                                                .15,
                                                .2,
                                                .15,
                                                .15,
                                                .2)
                                                , exact.vals = exact_val
                                                , file.name = session)
                            }
                            seqout$x[seqout$x['ID'] == id , "Tr"]
                            }
                           ''')

            r_f = robjects.r['f']
            out = r_f(cap_id, py_exact_var, py_exact_val, py_session)
            resp.body = 'Treatment=' + str(out[0])
        else:
            resp.body = 'Treatment=' + "error: party=" + req.params["party"]
        
# falcon.API instances are callable WSGI apps
app = falcon.API()

app.add_route('/test', DiagResource())
