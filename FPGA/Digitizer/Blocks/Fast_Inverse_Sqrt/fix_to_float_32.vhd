----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : 
-- Create Date: 07/27/2018
-- Description : change the input bit_vector to IEEE745 32bit floating point form. 1 sign 8 exponent 23 mantissa 
----------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;

entity fix_to_flo_32 is
  Port (
		D_in   : in std_logic_vector(31 downto 0);        
		D_out_flt  : out std_logic_vector(31 downto 0):= (others =>'0');
		D_out      : out std_logic_vector(15 downto 0):= (others =>'0');
		rst : in std_logic;
		clk : in std_logic
		
		-- sign_out : out std_logic :='0';
		-- exp_out  : out std_logic_vector(7 downto 0)  :=(others =>'0');
		-- mants_out: out std_logic_vector(22 downto 0) :=(others =>'0')
		
	);
end fix_to_flo_32 ;

architecture fpga of fix_to_flo_32 is

begin

  process(rst,clk)
	variable sign : std_logic :='0';
	variable exp  : std_logic_vector(7 downto 0)  :=(others =>'0');
	variable mants: std_logic_vector(22 downto 0) :=(others =>'0');
	variable D_abs: std_logic_vector(31 downto 0) :=(others =>'0');
	variable MSB  : integer range 0 to 31 :=0 ;
  begin
	if rst='1' then
		sign :='0';
		exp  := (others =>'0');
		mants:= (others =>'0');
		D_abs:= (others =>'0');
		MSB  :=0;
		D_out <= (others =>'0');
    else
        if(clk'event and clk = '1') then
			D_out <=D_in(31 downto 16);
			if D_in(31)='0' then 
				sign  := '0';
				D_abs := D_in;
			else
				sign  := '1';
				D_abs := not D_in+1;
			end if;
			
			for i in 0 to 31 loop
				if D_abs(i) = '1' then 
					MSB:= i;
				end if;
			end loop;
			
			if MSB> 22 then
				mants:=  D_abs(MSB-1 downto MSB-23);
				
			elsif  MSB = 22 then
				mants :=  D_abs(21 downto 0)&'0';
			elsif  MSB = 21 then
				mants :=  D_abs(20 downto 0)&"00";
			elsif  MSB = 20 then
				mants :=  D_abs(19 downto 0)&"000";   --------------mants(22 downto 23-MSB) :=  D_abs(MSB-1 downto 0);
			elsif  MSB = 19 then                      --------------mants(22-MSB downto 0) := (others =>'0');
				mants :=  D_abs(18 downto 0)&"0000";
			elsif  MSB = 18 then
				mants :=  D_abs(17 downto 0)&"00000";
			elsif  MSB = 17 then
				mants :=  D_abs(16 downto 0)&"000000";
			elsif  MSB = 16 then
				mants :=  D_abs(15 downto 0)&"0000000";
			elsif  MSB = 15 then
				mants :=  D_abs(14 downto 0)&"00000000";
			elsif  MSB = 14 then
				mants :=  D_abs(13 downto 0)&"000000000";
			elsif  MSB = 13 then
				mants :=  D_abs(12 downto 0)&"0000000000";
			elsif  MSB = 12 then
				mants :=  D_abs(11 downto 0)&"00000000000";
			elsif  MSB = 11 then
				mants :=  D_abs(10 downto 0)&"000000000000";
			elsif  MSB = 10 then
				mants :=  D_abs( 9 downto 0)&"0000000000000";
			elsif  MSB =  9 then
				mants :=  D_abs( 8 downto 0)&"00000000000000";
			elsif  MSB =  8 then
				mants :=  D_abs( 7 downto 0)&"000000000000000";
			elsif  MSB =  7 then
				mants :=  D_abs( 6 downto 0)&"0000000000000000";
			elsif  MSB =  6 then
				mants :=  D_abs( 5 downto 0)&"00000000000000000";
			elsif  MSB =  5 then
				mants :=  D_abs( 4 downto 0)&"000000000000000000";
			elsif  MSB =  4 then
				mants :=  D_abs( 3 downto 0)&"0000000000000000000";
			elsif  MSB =  3 then
				mants :=  D_abs( 2 downto 0)&"00000000000000000000";
			elsif  MSB =  2 then
				mants :=  D_abs( 1 downto 0)&"000000000000000000000";
			elsif  MSB =  1 then
				mants :=  D_abs(0)&"0000000000000000000000";
			else
				mants := "00000000000000000000000";
			end if;
			
			exp := std_logic_vector(to_unsigned(MSB+127, 8));  --bias =127   
			
		end if;
	end if;
	D_out_flt <= sign&exp&mants;
	-- sign_out<=sign;
	-- exp_out <=exp;
	-- mants_out <= mants;
  end process;

end fpga;
			
		
				
				