# micropolisbudgetdialog.py
#
# Micropolis, Unix Version.  This game was released for the Unix platform
# in or about 1990 and has been modified for inclusion in the One Laptop
# Per Child program.  Copyright (C) 1989 - 2007 Electronic Arts Inc.  If
# you need assistance with this program, you may contact:
#   http://wiki.laptop.org/go/Micropolis  or email  micropolis@laptop.org.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with this program.  If
# not, see <http://www.gnu.org/licenses/>.
#
#             ADDITIONAL TERMS per GNU GPL Section 7
#
# No trademark or publicity rights are granted.  This license does NOT
# give you any right, title or interest in the trademark SimCity or any
# other Electronic Arts trademark.  You may not distribute any
# modification of this program using the trademark SimCity or claim any
# affliation or association with Electronic Arts Inc. or its employees.
#
# Any propagation or conveyance of this program must include this
# copyright notice and these terms.
#
# If you convey this program (or any modifications of it) and assume
# contractual liability for the program to recipients of it, you agree
# to indemnify Electronic Arts for any liability that those contractual
# assumptions impose on Electronic Arts.
#
# You may not misrepresent the origins of this program; modified
# versions of the program must be marked as such and not identified as
# the original program.
#
# This disclaimer supplements the one included in the General Public
# License.  TO THE FULLEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW, THIS
# PROGRAM IS PROVIDED TO YOU "AS IS," WITH ALL FAULTS, WITHOUT WARRANTY
# OF ANY KIND, AND YOUR USE IS AT YOUR SOLE RISK.  THE ENTIRE RISK OF
# SATISFACTORY QUALITY AND PERFORMANCE RESIDES WITH YOU.  ELECTRONIC ARTS
# DISCLAIMS ANY AND ALL EXPRESS, IMPLIED OR STATUTORY WARRANTIES,
# INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY,
# FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OF THIRD PARTY
# RIGHTS, AND WARRANTIES (IF ANY) ARISING FROM A COURSE OF DEALING,
# USAGE, OR TRADE PRACTICE.  ELECTRONIC ARTS DOES NOT WARRANT AGAINST
# INTERFERENCE WITH YOUR ENJOYMENT OF THE PROGRAM; THAT THE PROGRAM WILL
# MEET YOUR REQUIREMENTS; THAT OPERATION OF THE PROGRAM WILL BE
# UNINTERRUPTED OR ERROR-FREE, OR THAT THE PROGRAM WILL BE COMPATIBLE
# WITH THIRD PARTY SOFTWARE OR THAT ANY ERRORS IN THE PROGRAM WILL BE
# CORRECTED.  NO ORAL OR WRITTEN ADVICE PROVIDED BY ELECTRONIC ARTS OR
# ANY AUTHORIZED REPRESENTATIVE SHALL CREATE A WARRANTY.  SOME
# JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF OR LIMITATIONS ON IMPLIED
# WARRANTIES OR THE LIMITATIONS ON THE APPLICABLE STATUTORY RIGHTS OF A
# CONSUMER, SO SOME OR ALL OF THE ABOVE EXCLUSIONS AND LIMITATIONS MAY
# NOT APPLY TO YOU.


########################################################################
# Micropolis Budget Dialog
# Bryan Cain


########################################################################
# Import stuff


import gtk
import cairo
import pango
import micropolisengine
import micropolisview
import sys, traceback


########################################################################
# MicropolisBudgetDialog


class MicropolisBudgetDialog(object):
    def __init__(self, engine, builder):
        self.engine = engine
        self.builder = builder

        self.engine.expressInterest(
            self,
            ('taxRate', 'budget',))

        # Views

        # Taxes Collected: $
        # Cash Flow: $
        # Previous Funds: $
        # Current Funds: $
        self.labelBudget1 = builder.get_object('budgetTaxesCollectedAmount')
        self.labelBudget2 = builder.get_object('budgetCashFlowAmount')
        self.labelBudget3 = builder.get_object('budgetPreviousFundsAmount')
        self.labelBudget4 = builder.get_object('budgetCurrentFundsAmount')

        scaleTaxRate = builder.get_object('budgetTaxRateScale')
        self.scaleTaxRate = scaleTaxRate
        scaleTaxRate.set_digits(0)
        scaleTaxRate.set_draw_value(False)
        scaleTaxRate.set_value_pos(1)
        scaleTaxRate.set_range(0, 20)
        scaleTaxRate.set_increments(1, 5)
        scaleTaxRate.set_value(engine.cityTax)
        scaleTaxRate.connect('value-changed', self.taxScaleChanged)

        self.labelTaxRate2 = builder.get_object('budgetTaxRatePercentLabel')
        self.labelFireFund = builder.get_object('budgetFireRequested')
        self.labelFireAlloc = builder.get_object('budgetFireAllocated')

        scaleFirePercent = builder.get_object('budgetFireFundingScale')
        self.scaleFirePercent = scaleFirePercent
        scaleFirePercent.set_digits(0)
        scaleFirePercent.set_draw_value(False)
        scaleFirePercent.set_value_pos(1)
        scaleFirePercent.set_range(0, 100)
        scaleFirePercent.set_increments(1, 10)
        scaleFirePercent.connect('value-changed', self.fireScaleChanged)

        self.labelFirePercent = builder.get_object('budgetFireFundingPercent')
        self.labelPoliceFund = builder.get_object('budgetPoliceRequested')
        self.labelPoliceAlloc = builder.get_object('budgetPoliceAllocated')

        scalePolicePercent = builder.get_object('budgetPoliceFundingScale')
        self.scalePolicePercent = scalePolicePercent
        scalePolicePercent.set_digits(0)
        scalePolicePercent.set_draw_value(False)
        scalePolicePercent.set_value_pos(1)
        scalePolicePercent.set_range(0, 100)
        scalePolicePercent.set_increments(1, 10)
        scalePolicePercent.connect('value-changed', self.policeScaleChanged)

        self.labelPolicePercent = builder.get_object('budgetPoliceFundingPercent')
        self.labelRoadFund = builder.get_object('budgetTransRequested')
        self.labelRoadAlloc = builder.get_object('budgetTransAllocated')

        scaleRoadPercent = builder.get_object('budgetTransFundingScale')
        self.scaleRoadPercent = scaleRoadPercent
        scaleRoadPercent.set_digits(0)
        scaleRoadPercent.set_draw_value(False)
        scaleRoadPercent.set_value_pos(1)
        scaleRoadPercent.set_range(0, 100)
        scaleRoadPercent.set_increments(1, 10)
        scaleRoadPercent.connect('value-changed', self.roadScaleChanged)

        self.labelRoadPercent = builder.get_object('budgetTransFundingPercent')

        self.update('taxRate')
        self.update('budget')

        self.actualDialog = self.builder.get_object('budgetDialog')
        self.actualDialog.set_title('City Budget for ' + str(self.engine.cityYear))

    def run(self):
        self.actualDialog.run()
    
    def hide(self):
        self.actualDialog.hide()

    def update(
        self,
        name,
        *args):

        engine = self.engine

        if name  == 'taxRate':

            taxRate = engine.cityTax
            scaleTaxRate = self.scaleTaxRate
            if scaleTaxRate.get_value() != taxRate:
                scaleTaxRate.set_value(taxRate)
            label = str(taxRate) + '%'
            self.labelTaxRate2.set_text(label)

        elif name == 'budget':

            formatMoney = engine.formatMoney
            formatPercent = engine.formatPercent

            totalFunds = engine.totalFunds
            taxFund = engine.taxFund
            fireFund = engine.fireFund
            fireValue = engine.fireValue
            firePercent = engine.firePercent
            policeFund = engine.policeFund
            policeValue = engine.policeValue
            policePercent = engine.policePercent
            roadFund = engine.roadFund
            roadValue = engine.roadValue
            roadPercent = engine.roadPercent

            cashFlow = (
                taxFund -
                fireValue -
                policeValue -
                roadValue)

            cashFlow2 = cashFlow

            if cashFlow == 0:
                cashFlowString = "$0"
            elif cashFlow > 0:
                cashFlowString = "+" + formatMoney(cashFlow)
            else:
                cashFlowString = "-" + formatMoney(-cashFlow)

            previousString = formatMoney(totalFunds)
            currentString = formatMoney(cashFlow2 + totalFunds)
            collectedString = formatMoney(taxFund)

            fireWantString = formatMoney(fireFund)
            firePercentString = formatPercent(firePercent)
            fireGotString = formatMoney(int(fireFund * firePercent))

            policeWantString = formatMoney(policeFund)
            policePercentString = formatPercent(policePercent)
            policeGotString = formatMoney(int(fireFund * policePercent))

            roadWantString = formatMoney(roadFund)
            roadPercentString = formatPercent(roadPercent)
            roadGotString = formatMoney(int(roadFund * roadPercent))

            self.labelBudget1.set_text(collectedString)
            self.labelBudget2.set_text(cashFlowString)
            self.labelBudget3.set_text(previousString)
            self.labelBudget4.set_text(currentString)

            self.labelFireFund.set_text(fireWantString)
            self.labelFireAlloc.set_text(fireGotString)
            self.labelFirePercent.set_text(firePercentString)
            value = int(firePercent * 100.0)
            if self.scaleFirePercent.get_value() != value:
                self.scaleFirePercent.set_value(value)

            self.labelPoliceFund.set_text(policeWantString)
            self.labelPoliceAlloc.set_text(policeGotString)
            self.labelPolicePercent.set_text(policePercentString)
            value = int(policePercent * 100.0)
            if self.scalePolicePercent.get_value() != value:
                self.scalePolicePercent.set_value(value)

            self.labelRoadFund.set_text(roadWantString)
            self.labelRoadAlloc.set_text(roadGotString)
            self.labelRoadPercent.set_text(roadPercentString)
            value = int(roadPercent * 100.0)
            if self.scaleRoadPercent.get_value() != value:
                self.scaleRoadPercent.set_value(value)


    def taxScaleChanged(self, scale):
        engine = self.engine
        tax = int(scale.get_value())
        if tax != engine.cityTax:
            engine.setCityTax(tax)


    def fireScaleChanged(self, scale):
        engine = self.engine
        fire = scale.get_value() / 100.0
        engine.firePercent = fire
        engine.fireSpend = int(fire * engine.fireFund)
        engine.updateFundEffects()
        engine.mustDrawBudget = True


    def policeScaleChanged(self, scale):
        engine = self.engine
        police = scale.get_value() / 100.0
        engine.policePercent = police
        engine.policeSpend = int(police * engine.policeFund)
        engine.updateFundEffects()
        engine.mustDrawBudget = True


    def roadScaleChanged(self, scale):
        engine = self.engine
        road = scale.get_value() / 100.0
        engine.roadPercent = road
        engine.roadSpend = int(road * engine.roadFund)
        engine.updateFundEffects()
        engine.mustDrawBudget = True


########################################################################
