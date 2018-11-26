----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : 
-- Create Date: 09/26/2018
-- Description : When Trig=1, Adr++ 
---------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
USE IEEE.STD_LOGIC_unsigned.ALL;

entity Trig_AdrPlus_v2 is

  port(
	Trig : in std_logic;    
	rst  : in std_logic;
	clk : in std_logic;
	Adr   : out std_logic_vector(12 downto 0):="0000000000000"
  );
  
end Trig_AdrPlus_v2;
  
architecture fpga of Trig_AdrPlus_v2 is

	

begin

  process(clk,rst)
	variable count : integer := 0;  
  begin 
    if rst='1'  then
		count := 0;
		Adr   <= "0000000000000";
	else
        if(clk'event and clk = '1' ) then
			if Trig ='1' then
				count := count +1;
			else
				count := count;
			end if;
			if count > 0 then
				Adr   <= std_logic_vector(to_unsigned(count-1, 13));
			else
				Adr   <= "0000000000000";
			end if;
		end if;
		
	end if;
  end process;
  
end fpga;