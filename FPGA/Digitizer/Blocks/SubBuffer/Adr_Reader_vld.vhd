----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference :
-- Create Date: 08/18/2018
-- Description : When vld is 1. Out put the address from where the DAQ should read data(form Dual Port RAM)
------------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;


entity Adr_Reader_vld is
  Port (
		vld   : in std_logic;
		Adr  : out std_logic_vector(9 downto 0) :=(others =>'0');
		
		rst : in std_logic;
		clk : in std_logic				
	);
end Adr_Reader_vld;

architecture fpga of Adr_Reader_vld is
	
	signal count : integer :=0;
	
	
begin
  process(rst,clk,vld)
  begin
	if rst='1' then
		Adr  <=(others =>'0');
		count <= 0;
    else
		if(clk'event and clk = '1' ) then
			if vld = '1' then 
				if count < 1023 then
					count <= count +1;
				else
					count <= 0;
				end if;
			else 
				count <= 0;
			end if;
			Adr <= std_logic_vector(to_unsigned(count, 10));
		end if;
	end if;
  end process;
 
end fpga;

				
		
		
		
		
		
		