----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : 
-- Create Date: 08/24/2018
-- Description : Selecte the RAM to put in data.
---------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
USE IEEE.STD_LOGIC_unsigned.ALL;

entity RAM_Selector is

  port(
	rst  : in std_logic;
	clk  : in std_logic;
	Adr  : in std_logic_vector(15 downto 0);
	vld_0   : out std_logic := '0';
	vld_1   : out std_logic := '0';
	vld_2   : out std_logic := '0';
	vld_3   : out std_logic := '0';
	vld_4   : out std_logic := '0'
	
  );
  
end RAM_Selector;
  
architecture fpga of RAM_Selector is
begin

  process(clk,rst)
	  
  begin 
    if rst='1'  then
		vld_0 <= '0';
		vld_1 <= '0';
		vld_2 <= '0';
		vld_3 <= '0';
		vld_4 <= '0';

	else
		if(clk'event and clk = '1' ) then
			if to_integer(unsigned(Adr)) mod 5 =0 then
				vld_0 <= '1';
				vld_1 <= '0';
				vld_2 <= '0';
				vld_3 <= '0';
				vld_4 <= '0';
			elsif to_integer(unsigned(Adr)) mod 5 =1 then
				vld_0 <= '0';
				vld_1 <= '1';
				vld_2 <= '0';
				vld_3 <= '0';
				vld_4 <= '0';
			elsif to_integer(unsigned(Adr)) mod 5 =2 then
				vld_0 <= '0';
				vld_1 <= '0';
				vld_2 <= '1';
				vld_3 <= '0';
				vld_4 <= '0';
			elsif to_integer(unsigned(Adr)) mod 5 =3 then
				vld_0 <= '0';
				vld_1 <= '0';
				vld_2 <= '0';
				vld_3 <= '1';
				vld_4 <= '0';
			elsif to_integer(unsigned(Adr)) mod 5 =4 then
				vld_0 <= '0';
				vld_1 <= '0';
				vld_2 <= '0';
				vld_3 <= '0';
				vld_4 <= '1';
			end if;
		end if;
	end if;
  end process;
  
end fpga;