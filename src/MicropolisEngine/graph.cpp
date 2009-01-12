/* graph.cpp
 *
 * Micropolis, Unix Version.  This game was released for the Unix platform
 * in or about 1990 and has been modified for inclusion in the One Laptop
 * Per Child program.  Copyright (C) 1989 - 2007 Electronic Arts Inc.  If
 * you need assistance with this program, you may contact:
 *   http://wiki.laptop.org/go/Micropolis  or email  micropolis@laptop.org.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.  You should have received a
 * copy of the GNU General Public License along with this program.  If
 * not, see <http://www.gnu.org/licenses/>.
 *
 *             ADDITIONAL TERMS per GNU GPL Section 7
 *
 * No trademark or publicity rights are granted.  This license does NOT
 * give you any right, title or interest in the trademark SimCity or any
 * other Electronic Arts trademark.  You may not distribute any
 * modification of this program using the trademark SimCity or claim any
 * affliation or association with Electronic Arts Inc. or its employees.
 *
 * Any propagation or conveyance of this program must include this
 * copyright notice and these terms.
 *
 * If you convey this program (or any modifications of it) and assume
 * contractual liability for the program to recipients of it, you agree
 * to indemnify Electronic Arts for any liability that those contractual
 * assumptions impose on Electronic Arts.
 *
 * You may not misrepresent the origins of this program; modified
 * versions of the program must be marked as such and not identified as
 * the original program.
 *
 * This disclaimer supplements the one included in the General Public
 * License.  TO THE FULLEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW, THIS
 * PROGRAM IS PROVIDED TO YOU "AS IS," WITH ALL FAULTS, WITHOUT WARRANTY
 * OF ANY KIND, AND YOUR USE IS AT YOUR SOLE RISK.  THE ENTIRE RISK OF
 * SATISFACTORY QUALITY AND PERFORMANCE RESIDES WITH YOU.  ELECTRONIC ARTS
 * DISCLAIMS ANY AND ALL EXPRESS, IMPLIED OR STATUTORY WARRANTIES,
 * INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY,
 * FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OF THIRD PARTY
 * RIGHTS, AND WARRANTIES (IF ANY) ARISING FROM A COURSE OF DEALING,
 * USAGE, OR TRADE PRACTICE.  ELECTRONIC ARTS DOES NOT WARRANT AGAINST
 * INTERFERENCE WITH YOUR ENJOYMENT OF THE PROGRAM; THAT THE PROGRAM WILL
 * MEET YOUR REQUIREMENTS; THAT OPERATION OF THE PROGRAM WILL BE
 * UNINTERRUPTED OR ERROR-FREE, OR THAT THE PROGRAM WILL BE COMPATIBLE
 * WITH THIRD PARTY SOFTWARE OR THAT ANY ERRORS IN THE PROGRAM WILL BE
 * CORRECTED.  NO ORAL OR WRITTEN ADVICE PROVIDED BY ELECTRONIC ARTS OR
 * ANY AUTHORIZED REPRESENTATIVE SHALL CREATE A WARRANTY.  SOME
 * JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF OR LIMITATIONS ON IMPLIED
 * WARRANTIES OR THE LIMITATIONS ON THE APPLICABLE STATUTORY RIGHTS OF A
 * CONSUMER, SO SOME OR ALL OF THE ABOVE EXCLUSIONS AND LIMITATIONS MAY
 * NOT APPLY TO YOU.
 */

/** @file graph.cpp */

////////////////////////////////////////////////////////////////////////


#include "stdafx.h"


////////////////////////////////////////////////////////////////////////


//char *Micropolis::HistName[] = {
//  "Residential", "Commercial", "Industrial",
//  "Cash Flow", "Crime", "Pollution"
//};

//unsigned char Micropolis::HistColor[] = {
//  COLOR_LIGHTGREEN, COLOR_DARKBLUE, COLOR_YELLOW,
//  COLOR_DARKGREEN, COLOR_RED, COLOR_OLIVE
//};


////////////////////////////////////////////////////////////////////////


/**
 * Copy history data to new array, scaling as needed.
 * @param hist  Source history data.
 * @param s     Destination byte array.
 * @param scale Scale factor.
 * @todo Figure out why we copy data.
 */
void Micropolis::drawMonth(short *hist, unsigned char *s, float scale)
{
    int val, x;

    for (x = 0; x < 120; x++) {
        val = (int)(hist[x] * scale);
        s[119 - x] = (unsigned char)clamp(val, 0, 255);
    }
}


/** Re-compute all graphs. */
void Micropolis::doAllGraphs()
{
    float scaleValue;
    short AllMax = 0;

    AllMax = max(AllMax, resHist10Max);
    AllMax = max(AllMax, comHist10Max);
    AllMax = max(AllMax, indHist10Max);

    if (AllMax <= 128) {
        AllMax = 0;
    }

    if (AllMax) {
        scaleValue = (float)128.0 / (float)AllMax;
    } else {
        scaleValue = 1.0;
    }

    // scaleValue = 0.5; // XXX

    drawMonth(resHist, History10[RES_HIST], scaleValue);
    drawMonth(comHist, History10[COM_HIST], scaleValue);
    drawMonth(indHist, History10[IND_HIST], scaleValue);
    drawMonth(moneyHist, History10[MONEY_HIST], 1.0);
    drawMonth(crimeHist, History10[CRIME_HIST], 1.0);
    drawMonth(pollutionHist, History10[POLLUTION_HIST], 1.0);

    AllMax = 0;

    AllMax = max(AllMax, resHist120Max);
    AllMax = max(AllMax, comHist120Max);
    AllMax = max(AllMax, indHist120Max);

    if (AllMax <= 128) {
        AllMax = 0;
    }

    if (AllMax) {
        scaleValue =
            (float)128.0 /
            (float)AllMax;
    } else {
        scaleValue =
            (float)1.0;
    }

    // scaleValue = 0.5; // XXX

    drawMonth(resHist + 120, History120[RES_HIST], scaleValue);
    drawMonth(comHist + 120, History120[COM_HIST], scaleValue);
    drawMonth(indHist + 120, History120[IND_HIST], scaleValue);
    drawMonth(moneyHist + 120, History120[MONEY_HIST], 1.0);
    drawMonth(crimeHist + 120, History120[CRIME_HIST], 1.0);
    drawMonth(pollutionHist + 120, History120[POLLUTION_HIST], 1.0);
}


/** Set flag that graph data has been changed and graphs should be updated. */
void Micropolis::ChangeCensus()
{
    censusChanged = true;
}


/**
 * If graph data has been changed, update all graphs.
 * If graphs have been changed, tell the user front-end about it.
 */
void Micropolis::graphDoer()
{
    if (censusChanged) {
        doAllGraphs();
        newGraph = true;
        censusChanged = false;
    }

    if (newGraph) {
        Callback("UIUpdate", "s", "graph");
        newGraph = false;
    }
}


/** Initialize graphs */
void Micropolis::initGraphs()
{
    if (!HistoryInitialized) {
        HistoryInitialized = 1;
    }
}


/** Compute various max ranges of graphs */
void Micropolis::InitGraphMax()
{
    int x;

    resHist10Max = 0;
    comHist10Max = 0;
    indHist10Max = 0;

    for (x = 118; x >= 0; x--) {

        resHist10Max = max(resHist10Max, resHist[x]);
        comHist10Max = max(comHist10Max, comHist[x]);
        indHist10Max = max(indHist10Max, indHist[x]);

        if (resHist[x] < 0) {
            resHist[x] = 0;
        }

        if (comHist[x] < 0) {
            comHist[x] = 0;
        }

        if (indHist[x] < 0) {
            indHist[x] = 0;
        }

    }

    Graph10Max = resHist10Max;

    if (comHist10Max > Graph10Max) {
        Graph10Max = comHist10Max;
    }

    if (indHist10Max > Graph10Max) {
        Graph10Max = indHist10Max;
    }

    resHist120Max = 0;
    comHist120Max = 0;
    indHist120Max = 0;

    for (x = 238; x >= 120; x--) {

        resHist120Max = max(resHist120Max, resHist[x]);
        comHist120Max = max(comHist120Max, comHist[x]);
        indHist120Max = max(indHist120Max, indHist[x]);

        if (resHist[x] < 0) {
            resHist[x] = 0;
        }

        if (comHist[x] < 0) {
            comHist[x] = 0;
        }

        if (indHist[x] < 0) {
            indHist[x] = 0;
        }

    }

    Graph120Max = resHist120Max;
    Graph120Max = max(Graph120Max, comHist120Max);
    Graph120Max = max(Graph120Max, indHist120Max);
}


////////////////////////////////////////////////////////////////////////
