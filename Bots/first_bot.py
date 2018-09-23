# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 19:54:58 2018

@author: jlasek
"""

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR


class LasekBot(sc2.BotAI):
    async def on_step(self, iteration):
        # What to do on every step
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.attack_if_no_nexus()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()

    ##################################################
    ############End of game single step###############
    ##################################################

    async def attack_if_no_nexus(self):
        if not self.units(NEXUS).ready.exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
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


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, LasekBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)