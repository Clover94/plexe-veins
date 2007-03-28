/* -*- mode:c++ -*- ********************************************************
 * file:        BaseLocAppl.cc
 *
 * author:      Peterpaul Klein Haneveld
 *
 * copyright:   (C) 2006 Parallel and Distributed Systems Group (PDS) at
 *              Technische Universiteit Delft, The Netherlands.
 *
 *              This program is free software; you can redistribute it 
 *              and/or modify it under the terms of the GNU General Public 
 *              License as published by the Free Software Foundation; either
 *              version 2 of the License, or (at your option) any later 
 *              version.
 *              For further information see file COPYING 
 *              in the top level directory
 ***************************************************************************
 * description: basic localization application class
 *              extend to create localization algorithm
 **************************************************************************/

#include "BaseLocAppl.h"

Define_Module(BaseLocAppl);

void BaseLocAppl::initialize(int stage)
{
	BaseModule::initialize(stage);

	if (stage == 0) {
		headerLength = par("headerLength");
		lowergateOut = findGate("lowergateOut");
		lowergateIn = findGate("lowergateIn");
		lowerControlIn = findGate("lowerControlIn");
		lowerControlOut = findGate("lowerControlOut");
		locgateIn = findGate("locgateIn");
		locgateOut = findGate("locgateOut");
	}
}

void BaseLocAppl::handleMessage(cMessage * msg)
{
	if (msg->arrivalGateId() == lowergateIn) {
		handleLowerMsg(msg);
	} else if (msg->arrivalGateId() == lowerControlIn) {
		EV << "handle lower control" << endl;
		handleLowerControl(msg);
	} else if (msg->arrivalGateId() == locgateIn) {
		EV << "handle localization message" << endl;
		handleLocMsg(msg);
	} else {
		handleSelfMsg(msg);
	}
}

void BaseLocAppl::sendDown(cMessage * msg)
{
	send(msg, lowergateOut);
}

void BaseLocAppl::sendDelayedDown(cMessage * msg, double delay)
{
	sendDelayed(msg, delay, lowergateOut);
}

void BaseLocAppl::sendControlDown(cMessage * msg)
{
	send(msg, lowerControlOut);
}

void BaseLocAppl::sendLoc(cMessage * msg)
{
	send(msg, locgateOut);
}