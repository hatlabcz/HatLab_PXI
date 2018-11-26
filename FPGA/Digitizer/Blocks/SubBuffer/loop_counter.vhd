----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : 
-- Create Date: 08/24/2018
-- Description : out put count + 1 at each clock cycle. Start from "min", after "max" is reached, count from "min" again.
---------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
USE IEEE.STD_LOGIC_unsigned.ALL;

entity loop_counter is

  port(
	rst  : in std_logic;
	clk  : in std_logic;
	min  : in std_logic_vector(15 downto 0);
	max  : in std_logic_vector(15 downto 0);
	count   : out std_logic_vector(15 downto 0)
  );
  
end loop_counter;
  
architecture fpga of loop_counter is
	signal counter : integer := 0;
begin

  process(clk,rst)
	  
  begin 
    if rst='1'  then
		counter <= 0;
		count   <= min;
	else
		if(clk'event and clk = '1' ) then
			if counter <to_integer(unsigned(max+not min + 1)) then
				counter <= counter+1;
			else
				counter <= 0;
			end if;
		count <= std_logic_vector(to_unsigned(counter, 16))+min;
		end if;
	end if;
  end process;
  
end fpga;