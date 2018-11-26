----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference :
-- Create Date: 08/17/2018
-- Description : When DAQ_read trigger is received. Output VLD=1 for 1002 cycles
------------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;


entity Trig_VLD is
  Port (
		DAQ_trig   : in std_logic;         --
		VLD  : out std_logic :='0';
		
		rst : in std_logic;
		clk : in std_logic				
	);
end Trig_VLD;

architecture fpga of Trig_VLD is
	
	signal count : integer :=0;
	signal vld_temp : std_logic :='0';
	
	
begin
  process(rst,DAQ_trig,clk)
  begin
	if rst='1' then
		count <= 0;
		vld  <= '0';
		vld_temp  <= '0';
    else
		if(DAQ_trig = '1') then
			count <= 0;
			vld_temp <= '1';
			vld  <= '1';
		else
			if(clk'event and clk = '1') then
				if vld_temp = '1' then
					count <= count +1;
					if count <1000 then
						vld_temp <= '1';
					else
						vld_temp <= '0';
					end if;
				else 
					vld_temp <= '0';
					count <= 0;
				end if;
			vld <= vld_temp;
			end if;
		end if;
	end if;
  end process;
 
end fpga;

				
		
		
		
		
		
		