% MATLAB file for running SSP

% S = [2, 5, 9]
SSP=SubSumNetworkClass([2, 5, 9])
Figure=SSP.drawNetwork
Figure.Visible='on'
Figure=SSP.multisim('Iterations', 10)
Figure.Visible='on'

