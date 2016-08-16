__author__ = 'sam.royston'
from mta.turnstile_synch import UpdateManager
from transport import transit

update_manager = UpdateManager(start_yr=15)
update_manager.clean_empties()
# update_manager.synch_turnstiles()
update_manager.synch_locations()
update_manager.synch_gtfs()

transit.run_opts()
