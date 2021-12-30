'''
Created on Jul 23, 2020

@author: willg
'''
#Module with functions for verifying room information
from UserDataProcessing import lounge_add
from collections import defaultdict
import common

_SINGLE_BLANK_RACE_TIME = 11
_MULTIPLE_BLANK_RACE_TIMES = 12
_ENTIRE_ROOM_BLANK_RACE_TIMES = 13
_WRONG_PLAYER_COUNT_GP_START = 21
_WRONG_PLAYER_COUNT_RACE = 22
_SINGLE_LARGE_TIME = 31
_MULTIPLE_LARGE_TIMES = 32
_RACERS_TIED = 41
_PLAYERS_CHANGED_DURING_GP = 51
_TABLE_EDITED = 61
_ROOM_SIZE_EDITED = 62
_MULTIPLE_RACES_WITH_SAME_TIMES = 71
_LARGE_DELTA_OCURRED = 72

EC_Messages = {_SINGLE_BLANK_RACE_TIME: "Room had a single blank race time. If there were no disconnections, table unreliable for this GP. If someone disconnected and DC points are being counted, this will count as a DC (and you can ignore this warning).",
               _MULTIPLE_BLANK_RACE_TIMES: "Room had a multiple blank race times (but not all times were blank). If there were no disconnections, table unreliable for this GP. If multiple people disconnected and DC points are being counted, these will count as a DCs (and you can ignore this warning).",
               _ENTIRE_ROOM_BLANK_RACE_TIMES: "Entire room had blank finish times. Could not determine actual results. Table unreliable for this GP.",
               _WRONG_PLAYER_COUNT_GP_START: "The number of players at the start of the GP does not match how many should be playing. If it was simply a disconnection, results should be reliable still. Otherwise, mkwx known bug #2.",
               _WRONG_PLAYER_COUNT_RACE: "The number of players doesn't match how many should be playing.",
               _SINGLE_LARGE_TIME : "One player had a large finish time (anti-cheat or mkwx error). Table unreliable for this GP.",
               _MULTIPLE_LARGE_TIMES : "Multiple players had large finish times (anti-cheat or mkwx error). Table unreliable for this GP.",
               _RACERS_TIED:"2 or more racers finished with the exact same time.",
               _MULTIPLE_RACES_WITH_SAME_TIMES:"",
               _LARGE_DELTA_OCURRED:""}

EC_Messages_Alternative = {_SINGLE_BLANK_RACE_TIME: "One blank race time. If no disconnections, table unreliable for this GP. If someone disconnected and DC points are being counted, this will count as a DC (and you can ignore this warning).",
               _MULTIPLE_BLANK_RACE_TIMES: "Room had a multiple blank race times (but not all times were blank). If there were no disconnections, table unreliable for this GP. If multiple people disconnected and DC points are being counted, these will count as a DCs (and you can ignore this warning).",
               _ENTIRE_ROOM_BLANK_RACE_TIMES: "Entire room had blank finish times. Could not determine actual results. Table unreliable for this GP.",
               _WRONG_PLAYER_COUNT_GP_START: "Players missing at the start of the GP (or disconnected race 1). If GP started with correct number and no DCs race 1, this is an mkwx bug.",
               _WRONG_PLAYER_COUNT_RACE: "One or more players missing.",
               _SINGLE_LARGE_TIME : "One player had a large finish time (mkwx error). Use ?quickedit to correct their position.",
               _MULTIPLE_LARGE_TIMES : "Multiple players had large finish times (mkwx error). Use ?quickedit to correct their positions.",
               _RACERS_TIED:"2 or more racers finished with the exact same time.",
               _MULTIPLE_RACES_WITH_SAME_TIMES:"",
               _LARGE_DELTA_OCURRED:""}

SUGGESTION_TYPES = { # ALL SUGGESTIONS WILL BE PLACED ON SEPARATE SECTIONS OF MESSAGE AND WILL HAVE A `REJECT` BUTTON IF THE USER WANTS TO REJECT A SUGGESTED FIX

    "gp_missing", #player(s) missing at the start of a GP (button for ?earlydc if only one player is missing, if more select menu to change room size and button to confirm)
    "missing_player", #player is missing from race (2 buttons: 1 to choose DCed on, another to choose DCed before)
    "blank_player", #player had blank time in race (2 buttons: 1 to choose DCed on, another to choose before)
    "large_time", #player had large finish time (select menu to choose correct position)
    "tie", #players had tied finish times (select menus for user to put players in correct order / select menus to select each player's correct position)

}



def get_room_errors_players(war, room, error_types, startrace=None, endrace=None, lounge_replace=True, ignoreLargeTimes=False):   
    race_errors = {}
    
    if startrace is None:
        startrace = 1
    if endrace is None:
        endrace = len(room.races)
    startrace -= 1
    
    dc_on_or_before = room.dc_on_or_before
    
    for raceInd, race in enumerate(room.races[startrace:endrace], startrace):
        errors = []
        blank_time_counter = 0
        for placement in race.placements:
            if placement.is_disconnected():
                fc, name = placement.get_fc_and_name()
                
                if race.raceNumber in dc_on_or_before and fc in dc_on_or_before[race.raceNumber]:
                    stuffs = [4, 3, 2, 1]
                    numberOfDCPtsGivenMissing = war.missingRacePts * stuffs[(int(race.raceNumber)-1)%4]
                    numberOfDCPtsGivenOn = war.missingRacePts * stuffs[(int(race.raceNumber)-1)%4] - war.missingRacePts
                                
                    if dc_on_or_before[race.raceNumber][fc] == 'on':
                        errors.append(name + lounge_add(fc, lounge_replace) + " DCed and was on results (tabler confirmed). Giving " + str(numberOfDCPtsGivenOn) + " total DC points (3 per missing race). (" + str(len(race.placements)) + " players in room this race)")
                    else:
                        errors.append(name + lounge_add(fc, lounge_replace) + " DCed before this race (tabler confirmed). Giving " + str(numberOfDCPtsGivenMissing) + " total DC points (3 per missing race). (" + str(len(race.placements)) + " players in room this race)")
                else:
                    # if not race.raceNumber in dc_on_or_before or fc not in dc_on_or_before[race.raceNumber]:
                    err_mes = name + lounge_add(fc, lounge_replace) + " had a blank race time. Disconnected unless mkwx bug."
                    errors.append(err_mes + " Not giving DC points for this race - use ?dcs to fix this")
                    error_types[int(race.raceNumber)].append({'type': 'blank_player', 'player_name': name + lounge_add(fc, lounge_replace), 'player_fc': fc, 'message': err_mes})

                    blank_time_counter +=1 
            
            if not ignoreLargeTimes:
                if placement.is_bogus_time():
                    fc, name = placement.get_fc_and_name()
                    err_mes = name + lounge_add(fc, lounge_replace) + " had large finish time: " + placement.get_time_string() 
                    errors.append(err_mes + " - use ?qe to change their position")
                    error_types[int(race.raceNumber)].append(({'type': 'large_time', 'player_name': name + lounge_add(fc, lounge_replace), 'player_fc': fc, 'placements': list(range(1, len(race.placements)+1)),'message': err_mes}))

        ties = race.getTies()
        if len(ties) > 0:
            error_type = {'type': 'tie', 'player_names': [], 'player_fcs': [], 'placements': []}
            errors.append("Ties occurred (check table for errors):")
            for this_fc in sorted(ties, key=lambda fc:race.getPlacement(fc)):
                this_placement = race.getPlacement(this_fc)
                _, this_name = this_placement.get_fc_and_name()
                errors.append(this_name + lounge_add(this_fc, lounge_replace) + "'s finish time: " + this_placement.get_time_string() + " - use ?qe to change their position")
                error_type['player_names'].append(this_name + lounge_add(this_fc, lounge_replace))
                error_type['player_fcs'].append(this_fc)
                error_type['placements'].append(this_placement.get_place())

            error_type['message'] = "Ties occurred between " + '  |  '.join(error_type['player_names'])
            error_types[int(race.raceNumber)].append(error_type)

        if blank_time_counter == len(race.placements):
            errors = [EC_Messages_Alternative[_ENTIRE_ROOM_BLANK_RACE_TIMES]]
        
            
        #Check if this race's times are the same as any of the previous races times (excluding blank times)
        prior_races = room.races[startrace:raceInd]
        for prior_race in prior_races:
            if race.times_are_subset_of_and_not_all_blank(prior_race):
                errors.append("This race had the exact same race times as a previous race. Table is incorrect for this GP.")
                
        if race.has_unusual_delta_time():
            errors.append("This race had players with impossible deltas (lag). Table could be incorrect for this GP.")
            
            
        errors.extend(room.get_subin_error_string_list(race.raceNumber))
            
        if race.raceNumber in room.forcedRoomSize:
            errors.append("Room size changed to " + str(room.forcedRoomSize[race.raceNumber]) + " players for this race.")
            for indx, err in enumerate(error_types[int(race.raceNumber)]):
                if err['type'] in ['blank_player', 'gp_missing']:
                    error_types[int(race.raceNumber)].pop(indx)
        
        if room.placements_changed_for_racenum(race.raceNumber):
            errors.append("Placements changed by tabler for this race.")
        
        #check if list is empty
        if len(errors) > 0:
            race_errors[int(race.raceNumber)] = errors
    
    
    return race_errors

def get_war_errors_players(war, room, error_types, lounge_replace=True, ignoreLargeTimes=False):
    if room is None or not room.is_initialized():
        return None
    
    race_errors = {}
    numberOfPlayers = war.numberOfTeams * war.playersPerTeam
    missingPlayersByRace = room.getMissingOnRace(war.getNumberOfGPS())

        
    startrace = 0
    endrace = war.getNumberOfGPS()*4
    dc_on_or_before = room.dc_on_or_before
    for race in room.races[startrace:endrace]:
        if race.getNumberOfPlayers() != numberOfPlayers:
            race_errors[int(race.raceNumber)] = []
            try:
                if ((int(race.raceNumber)-1) % 4) == 0:
                    err_mes = str(len(race.placements)) + " players at start of GP. Should have " + str(war.get_num_players()) + " players. "
                    race_errors[int(race.raceNumber)].append(err_mes + "Use ?earlydc if necessary.")
                    if race.raceNumber in room.forcedRoomSize:
                        init_str = "Room size confirmed as " if room.forcedRoomSize[race.raceNumber] == len(race.placements) else "Room size changed to "
                        race_errors[int(race.raceNumber)].append(init_str + str(room.forcedRoomSize[race.raceNumber]) + " players for this race.")
                    else:
                        error_types[int(race.raceNumber)].append({'type': 'gp_missing', 
                                                                    'num_missing': numberOfPlayers - race.getNumberOfPlayers(), 
                                                                    'corrected_room_sizes': list(range(race.getNumberOfPlayers(), war.get_num_players() +1)), 
                                                                    'message': err_mes})
                
                elif missingPlayersByRace[int(race.raceNumber)-1] != []:
                    for missingFC, missingName in missingPlayersByRace[int(race.raceNumber)-1]:
                        stuffs = [4, 3, 2, 1]
                        numberOfDCPtsGivenMissing = war.missingRacePts * stuffs[(int(race.raceNumber)-1)%4]
                        numberOfDCPtsGivenOn = war.missingRacePts * stuffs[(int(race.raceNumber)-1)%4] - war.missingRacePts
                        
                        if race.raceNumber in dc_on_or_before\
                            and missingFC in dc_on_or_before[race.raceNumber]:
                            # num_extra_players = 0
                            # for _, on_before in dc_on_or_before[race.raceNumber].items():
                            #     if on_before == 'on':
                            #         num_extra_players += 1
                                    
                            if dc_on_or_before[race.raceNumber][missingFC] == 'on':
                                race_errors[int(race.raceNumber)].append(missingName + lounge_add(missingFC, lounge_replace) + " DCed and was on results (tabler confirmed). Giving " + str(numberOfDCPtsGivenOn) + " total DC points (3 per missing race). (" + str(len(race.placements)) + " players in room this race)")
                            else:
                                race_errors[int(race.raceNumber)].append(missingName + lounge_add(missingFC, lounge_replace) + " DCed before this race (tabler confirmed). Giving " + str(numberOfDCPtsGivenMissing) + " total DC points (3 per missing race). (" + str(len(race.placements)) + " players in room this race)")
    
                        else:
                            err_mes = missingName + lounge_add(missingFC, lounge_replace) + " is missing. Giving " + str(war.missingRacePts) + " DC points per missing race."
                            race_errors[int(race.raceNumber)].append(err_mes + " (" + str(len(race.placements)) + " players in room) - Use ?dcs to fix this.")
                            error_types[int(race.raceNumber)].append({'type': 'missing_player', 
                                        'player_name': missingName + lounge_add(missingFC, lounge_replace), 
                                        'player_fc': missingFC,
                                        'message': err_mes})

                if not race_errors[int(race.raceNumber)]:
                    del race_errors[int(race.raceNumber)]
            except IndexError:
                common.log_text(str(missingPlayersByRace), common.ERROR_LOGGING_TYPE)
                common.log_text(str(race), common.ERROR_LOGGING_TYPE)
                raise
                
            
    by_gp = defaultdict(list)
    for race in room.races[startrace:endrace]:
        race_num = race.raceNumber
        gp_num = int((race_num-1)/4)
        by_gp[gp_num].append(race)
        
    for gp_num, gp in by_gp.items():
        if len(gp) >= 2:
            for index_num in range(1, len(gp)):
                if not set(gp[index_num].getFCs()).issubset(set(gp[index_num-1].getFCs())):
                    race_num = int(gp[index_num].raceNumber)
                    if race_num not in race_errors:
                        race_errors[race_num] = []
                    race_errors[race_num].append("Players in room changed mid-GP. THIS IS AN MKWX BUG. Table is incorrect for this GP.")      
                    
    for i in range(war.getNumberOfGPS()):
        if len(war.getEditsForGP(i+1)) > 0:
            GPRaceStart = (i*4) + 1
            if GPRaceStart not in race_errors:
                race_errors[GPRaceStart] = []
            race_errors[GPRaceStart].insert(0, "Table has been manually modified for this GP.")
            
    temp_dict = get_room_errors_players(war, room, error_types, startrace+1, endrace, lounge_replace=lounge_replace, ignoreLargeTimes=ignoreLargeTimes)
    
    for raceNum, ECs in temp_dict.items():
        if raceNum in race_errors:
            race_errors[raceNum].extend(ECs)
        else:
            race_errors[raceNum] = ECs
    return race_errors
    
            
        