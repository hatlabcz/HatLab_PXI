----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : 
-- Create Date: 08/12/2018
-- Description : Used to Count the Address in Dual_Port_RAM
---              When clock cycle < Read_start, the output(Read_Adr) will always be Read_AdrBegin (usually the value in address=Read_AdrBegin is set to 0)
---              When  Read_start < clock cycle < Read_stop , the output will +1 at each clock cycle.
---              When clock cycle > Read_stop , the output will  be Read_AdrBegin again
--------------------------Remember to use MUX right after the PCPort block if you want to read address 0X1000 or larger-----------------------
---------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
USE IEEE.STD_LOGIC_unsigned.ALL;

entity Adr_Counter_v3 is

  port(
	Read_start : in std_logic_vector(15 downto 0);    
	Read_stop  : in std_logic_vector(15 downto 0);    
	Read_AdrBegin: in std_logic_vector(9 downto 0);
	clk : in std_logic;
	rst : in std_logic;
	
	Read_Adr   : out std_logic_vector(9 downto 0)
  );
  
end Adr_Counter_v3;
  
architecture fpga of Adr_Counter_v3 is

	signal count : integer := 0;
	signal adr : std_logic_vector(9 downto 0):=(others => '0');

begin

  process(clk,rst)  
  begin 
    if rst='1'  then
		count <= 0;
		adr   <= Read_AdrBegin;
	else
        if(clk'event and clk='1') then
			if count < to_integer(unsigned(Read_start)) then
				count <= count + 1;
				adr   <= Read_AdrBegin;
			elsif count > to_integer(unsigned(Read_stop)) then
				adr   <= Read_AdrBegin;
			else 
				count <= count + 1;
				adr   <= adr + 1;
			end if;
		end if;
	end if;
  end process;
  
  Read_Adr <= adr;
end fpga;