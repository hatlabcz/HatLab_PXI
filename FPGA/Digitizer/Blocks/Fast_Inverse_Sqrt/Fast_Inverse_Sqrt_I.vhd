----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : "quake3-1.32b/code/game/q_math.c". Quake III Arena. id Software. Retrieved 2017-01-21.
-- Create Date: 07/27/2018
-- Description : Fast inverse square root, based on the reference.(Totally amazed, shocked and mindfucked)
----------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;

entity Inv_Sqrt_I is
  port(
    D_in_flt   : in std_logic_vector(31 downto 0);
	I_flt  : out std_logic_vector(31 downto 0) := (others =>'0');
	
	D_in  : in std_logic_vector(15 downto 0) := (others =>'0');
	D_out : out std_logic_vector(15 downto 0):= (others =>'0');
	
	rst : in std_logic;
	clk : in std_logic
  );
end Inv_Sqrt_I;

architecture fpga of Inv_Sqrt_I is

  constant M : std_logic_vector(31 downto 0) := "01011111001101110101100111011111";  --The Maaaaaaaaaaaaaaaag!c Number

  begin
  
  process(clk, rst)
	variable D2: std_logic_vector(31 downto 0) := (others =>'0');
  begin
	if rst='1' then
		D2    := (others =>'0');
		I_flt <= (others =>'0');
	    D_out <= (others =>'0');
    else
        if(clk'event and clk = '1') then
			D2    := '0'& D_in_flt(31 downto 1);   --D_in/2
			I_flt <= M + not D2 + 1;              ---- M-D2
			D_out <=D_in;
		end if;
	end if;
	
  end process;
end fpga;			
		
  
  


