----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference :
-- Create Date: 08/08/2018
-- Description : Used for reading the address in the Sin_generator block. The output(address) jumps between Start and Start+5 at each clock cycle
------------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;


entity jump_counter is
  Port (
		Start   : in std_logic_vector(9 downto 0);         
		Address   : out std_logic_vector(9 downto 0);
		
		rst : in std_logic;
		clk : in std_logic				
	);
end jump_counter;

architecture fpga of jump_counter is
  
  signal counter : integer :=0;

begin
  
  process(rst,clk) 
  begin
    if rst='1' then
		counter  <= 0;
		Address  <= Start;
    else
        if(clk'event and clk = '1') then
			if counter =0 then
				Address <=Start;
				counter <=1;
			else
				counter<=0;
				Address <=Start+"0000000101";
			end if;
		end if;
	end if;
  end process;
 
end fpga;

		