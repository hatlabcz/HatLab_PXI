----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : 
-- Create Date: 07/19/2018
-- Description : Used to find the most significance bits for both I and Q data( max(MSB_I, MSB_Q) ), since the truncation of I and Q should be the same. 
---              The input is the first 17 bits of the 32bit output from the integration block.

---------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

entity FIND_MSB_IQ is
  port(
    Din_I : in std_logic_vector(16 downto 0);
	Din_Q : in std_logic_vector(16 downto 0);
	
	Dout: out std_logic_vector(4 downto 0):="01111";  -- unsigned
    
	clk : in std_logic;
	rst : in std_logic
  
  );
end FIND_MSB_IQ;

architecture behave of FIND_MSB_IQ is
  
  Signal MSB_temp : std_logic_vector(4 downto 0)  :="01111";
  signal bar      : std_logic_vector(16 downto 0)  :=(others => '0');
  signal Din_abs_I  : std_logic_vector(16 downto 0) :=(others => '0');
  signal Din_abs_Q  : std_logic_vector(16 downto 0) :=(others => '0');
  signal Din_abs    : std_logic_vector(16 downto 0) :=(others => '0');  -- max(Din_abs_I,Din_abs_Q)
  
begin

  Din_abs_I <= not Din_I  when Din_I(16)='1' else Din_I;
  Din_abs_Q <= not Din_Q  when Din_Q(16)='1' else Din_Q;
  Din_abs   <= Din_abs_I  when unsigned(Din_abs_I) > unsigned(Din_abs_Q) else Din_abs_Q;
  
  
  process(clk, rst)
  begin
    if(rst = '1') then
			MSB_temp <= "01111";
			bar <= (others => '0');
			
	else
		if(clk'event and clk = '1') then
			if (to_integer(unsigned(Din_abs))-to_integer(unsigned(bar))>0) then
				bar <= Din_abs;
				if Din_abs(16 downto 15) = "01" then
					MSB_temp <= "11111";
				elsif Din_abs(16 downto 14) = "001" then
					MSB_temp <= "11110";
				elsif Din_abs(16 downto 13) = "0001" then
					MSB_temp <= "11101";
				elsif Din_abs(16 downto 12) = "00001" then
					MSB_temp <= "11100";
				elsif Din_abs(16 downto 11) = "000001" then
					MSB_temp <= "11011";
				elsif Din_abs(16 downto 10) = "0000001" then
					MSB_temp <= "11010";
				elsif Din_abs(16 downto  9) = "00000001" then
					MSB_temp <= "11001";
				elsif Din_abs(16 downto  8) = "000000001" then
					MSB_temp <= "11000";
				elsif Din_abs(16 downto  7) = "0000000001" then
					MSB_temp <= "10111";
				elsif Din_abs(16 downto  6) = "00000000001" then
					MSB_temp <= "10110";
				elsif Din_abs(16 downto  5) = "000000000001" then
					MSB_temp <= "10101";
				elsif Din_abs(16 downto  4) = "0000000000001" then
					MSB_temp <= "10100";
				elsif Din_abs(16 downto  3) = "00000000000001" then
					MSB_temp <= "10011";
				elsif Din_abs(16 downto  2) = "000000000000001" then
					MSB_temp <= "10010";
				elsif Din_abs(16 downto  1) = "0000000000000001" then
					MSB_temp <= "10001";
				elsif Din_abs(16 downto  0) = "00000000000000001" then
					MSB_temp <= "10000";
				else
					MSB_temp <= "01111";
				end if;
		    end if;
		end if;
	end if;
  end process;
  Dout <= MSB_temp ;
end behave;
