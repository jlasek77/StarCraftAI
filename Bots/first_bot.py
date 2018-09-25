# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 19:54:58 2018

@author: jlasek
"""
from typing import List

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, ROBOTICSFACILITY, ROBOTICSBAY, \
    STALKER, COLOSSUS, RESEARCH_EXTENDEDTHERMALLANCE, FORGE, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1


class LasekBot(sc2.BotAI):
    async def on_step(self, iteration):
        # What to do on every step
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.attack_if_no_nexus()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.build_gate()
        await self.build_cybernetics_core()
        await self.build_robotics_facility()
        await self.build_robotics_bay()
        await self.create_stalker()
        await self.create_colossus()
        await self.updgrade_robotics_bay()
        await self.create_more_gates()
        await self.build_and_upgrade_forge()

    ##################################################
    ########### End of game single step ##############
    ##################################################

    async def attack_if_no_nexus(self):
        if not self.units(NEXUS).ready.exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return

    # async def build_workers(self):
    #     for nexus in self.units(NEXUS).ready.noqueue:
    #         if self.can_afford(PROBE) and self.workers.amount < self.units(NEXUS).amount*16:
    #             await self.do(nexus.train(PROBE))

    async def build_workers(self):
        nexus = self.units(NEXUS).ready.random
        if self.workers.amount < self.units(NEXUS).amount * 20 and nexus.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        nexus = self.units(NEXUS).ready.random
        if self.supply_left < 3 and not self.already_pending(PYLON):
            if self.can_afford(PYLON):
                await self.build(PYLON, near=nexus.position.towards(self.game_info.map_center, 5))

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            vgs = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vg in vgs:
                if not self.can_afford(ASSIMILATOR):
                    break

                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                    await self.do(worker.build(ASSIMILATOR, vg))

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_gate(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if not self.units(GATEWAY).exists:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 3))

    async def build_cybernetics_core(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists:
                if not self.units(CYBERNETICSCORE).exists:
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon.position.towards(self.game_info.map_center, 5))

    async def build_robotics_facility(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists and self.units(CYBERNETICSCORE).ready.exists:
                if not self.units(ROBOTICSFACILITY).exists:
                    if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                        await self.build(ROBOTICSFACILITY, near=pylon.position.towards(self.game_info.map_center, 6))

    async def build_robotics_bay(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(ROBOTICSFACILITY).exists and self.can_afford(ROBOTICSBAY) and not self.already_pending(
                    ROBOTICSBAY) and self.units(ROBOTICSBAY).amount < 1:
                await  self.build(ROBOTICSBAY, near=pylon.position.towards(self.game_info.map_center, 7))

    async def create_stalker(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left > 0:
                await self.do(gw.train(STALKER))

    async def create_colossus(self):
        for rb in self.units(ROBOTICSFACILITY).ready.noqueue:
            if self.can_afford(COLOSSUS) and self.supply_left > 0:
                await self.do(rb.train(COLOSSUS))

    async def updgrade_robotics_bay(self):
        if self.units(ROBOTICSBAY).ready.exists:
            building = self.units(ROBOTICSBAY).ready.first
            # buildings = self.units(ROBOTICSBAY).ready.
            abilities = await self.get_available_abilities(building)
            if RESEARCH_EXTENDEDTHERMALLANCE in abilities:
                if self.can_afford(RESEARCH_EXTENDEDTHERMALLANCE) and building.noqueue:
                    await self.do(building(RESEARCH_EXTENDEDTHERMALLANCE))

    async def create_more_gates(self):
        if self.units(GATEWAY).ready.exists and self.minerals > 1000 and self.units(GATEWAY).amount < 4:
            pylon = self.units(PYLON).ready.random
            if not self.already_pending(GATEWAY):
                await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 3))

    async def build_and_upgrade_forge(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if not self.units(FORGE).exists:
                if self.can_afford(FORGE) and not self.already_pending(FORGE) and self.minerals > 1000:
                    await self.build(FORGE, near=pylon.position.towards(self.game_info.map_center, 3))
        if self.units(FORGE).ready.exists:
            building = self.units(FORGE).ready.first
            abilities = await self.get_available_abilities(building)
            for ability in abilities:
                if self.can_afford(ability) and building.noqueue:
                    await self.do(building(ability))




run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, LasekBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
