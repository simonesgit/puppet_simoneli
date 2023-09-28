function fn_comm_protocol_fix
{
fail_stage=
if grep protocol $HOME/ctm/data/CONFIG.dat |grep 11 ;
then
	echo Pre-Upgrade Identified Agent communication protocol still in 11, going to configure the value to minimum 12

	if ! ag_ping;
	then
		echo Pre-Upgrade ag_ping test failed before trying to configure Agent communication protocol from 11 to minimum 12.  No action performed, please contact support team for help.
		exit 21
	fi

	ctmcfg -table CONFIG -action UPDATE -parameter COMM_PROTOCOL -value 12

	if grep protocol $HOME/ctm/data/CONFIG.dat |grep 12;
	then
		if ag_ping;
		then 
			echo Pre-Upgrade Configure Agent communication protocol to 12 successfully. 
			return
		else 
			fail_stage=“ag_ping failed after configured protocol to 12”
		fi
	else
		fail_sate=“ctmcfg failed to configure protocol to 12”
	fi
else
	echo Pre-Upgrade Verified Agent communication protocol is on / above the minimum 12, ok to proceed next. 
	return
fi
ctmcfg -table CONFIG -action UPDATE -parameter COMM_PROTOCOL -value 11 
if  ! grep protocol $HOME/ctm/data/CONFIG.dat |grep 11;
then
	if ag_ping;
	then
		echo Pre-Upgrade Failed to configure Agent communication protocol to 12 due to ${fail_stage}, rollback to protocol 11 successfully. Please contact support team to configure the Agent communication protocol to the minimum 12 before upgrade. 
		exit 22
	else
		echo Pre-Upgrade Failed to configure Agent communication protocol to 12 due to ${fail_stage}, in addition ag_ping failed after rollbacked to protocol 11, please contact support team for help.
		exit 23
	fi
else
	echo Pre-Upgrade Failed to configure Agent communication protocol to 12 due to ${fail_stage}, current configuration -  $(grep protocol $HOME/ctm/data/CONFIG.dat), please contact support team for help.
fi


} 
