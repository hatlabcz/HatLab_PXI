----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : "quake3-1.32b/code/game/q_math.c". Quake III Arena. id Software. Retrieved 2017-01-21.
-- Create Date: 07/27/2018
-- Description : In last step we convert the initial guess into 16 bit unsigned vector. 
---              Now we do a final Newton iteration to get the final result.
----------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;

entity Inv_Sqrt_II is
  port(
	I_in   : in std_logic_vector(15 downto 0);
	D_in   : in std_logic_vector(15 downto 0);
	ISqrt_out  : out std_logic_vector(15 downto 0) := (others =>'0');
	
	rst : in std_logic;
	clk : in std_logic
  );
end Inv_Sqrt_II;

architecture fpga of Inv_Sqrt_II is

  constant threehalf : integer := 98304;
  signal Ithreehalf  : integer range 0 to 65536:=0;     --3/2 * I
  signal IDhalf      : integer range 0 to 65536:=0;    --1/2 * D * I
  signal II          : integer:=0;    --I *I
  
  

  begin
  
  process(clk, rst)
	variable Dhalf   : integer range 0 to 65536:= 0;
	variable Iint    : integer range 0 to 65536 := 0;
  begin
	if rst='1' then
		Dhalf    := 0;
		Iint	 := 0;
		Ithreehalf <= 0;
		IDhalf      <= 0;
		II         <= 0;
		ISqrt_out <= (others =>'0');
		
    else
        if(clk'event and clk = '1') then
			Dhalf    := to_integer(unsigned('0'& D_in(15 downto 1)));   --D_in/2
			Iint     := to_integer(unsigned(I_in));
			Ithreehalf  <= threehalf*Iint/65536;
			IDhalf      <= Dhalf*Iint/256;
			II          <= Iint*Iint/256;
			ISqrt_out  <= std_logic_vector(to_unsigned(Ithreehalf - IDhalf*II/65536,16));	
		end if;
	end if;
	
  end process;
end fpga;			
		
  
  


