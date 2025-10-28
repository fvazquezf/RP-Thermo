% General Thermometer Puzzle Rules (0-based)
% Thermometers and lengths are defined per dom file
% These will be imported from the encoded domXX.lp files

% Allowed fill lengths
allowed_length(T,I) :- len(T,L), index(I), I <= L.

% Choice rule: each thermometer picks exactly one fill length
1 { fill_len(T,I) : allowed_length(T,I) } 1 :- thermometer(T).

% Filled cells
fill(R,C) :- pos(T,I,R,C), fill_len(T,K), I <= K.

% Row and column constraints
:- rows(R), target_row(R,N), not N = #count { C : fill(R,C) }.
:- col(C), target_col(C,N), not N = #count { R : fill(R,C) }.

% Show output for decode.py
#show fill_len/2.
#show fill/2.
