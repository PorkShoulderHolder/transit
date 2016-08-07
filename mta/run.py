__author__ = 'sam.royston'
from turnstile_synch import UpdateManager
from transit import transit

update_manager = UpdateManager(start_yr=15)
# update_manager.synch_turnstiles()
# update_manager.synch_locations()
# update_manager.synch_gtfs()

transit.run_opts()