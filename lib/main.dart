import 'package:flutter/material.dart';

void main() {
  runApp(const CalculatorApp());
}

class CalculatorApp extends StatelessWidget {
  const CalculatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Calculator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF1C1C1E),
      ),
      home: const CalculatorScreen(),
    );
  }
}

class CalculatorScreen extends StatefulWidget {
  const CalculatorScreen({super.key});

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  String _display = '0';
  String _expression = '';
  double _firstOperand = 0;
  String _operator = '';
  bool _shouldResetDisplay = false;

  void _onDigitPressed(String digit) {
    setState(() {
      if (_display == '0' || _shouldResetDisplay) {
        _display = digit;
        _shouldResetDisplay = false;
      } else {
        if (_display.length < 12) {
          _display += digit;
        }
      }
    });
  }

  void _onDecimalPressed() {
    setState(() {
      if (_shouldResetDisplay) {
        _display = '0.';
        _shouldResetDisplay = false;
      } else if (!_display.contains('.')) {
        _display += '.';
      }
    });
  }

  void _onOperatorPressed(String operator) {
    if (_display == 'Error') return;
    setState(() {
      if (_operator.isNotEmpty && !_shouldResetDisplay) {
        _calculate();
        if (_display == 'Error') return;
      }
      _firstOperand = double.parse(_display);
      _operator = operator;
      _expression = '${_formatNumber(_firstOperand)} $operator';
      _shouldResetDisplay = true;
    });
  }

  void _calculate() {
    if (_operator.isEmpty || _display == 'Error') return;

    final secondOperand = double.parse(_display);
    double result = 0;

    switch (_operator) {
      case '+':
        result = _firstOperand + secondOperand;
        break;
      case '−':
        result = _firstOperand - secondOperand;
        break;
      case '×':
        result = _firstOperand * secondOperand;
        break;
      case '÷':
        if (secondOperand == 0) {
          setState(() {
            _display = 'Error';
            _expression = '';
            _operator = '';
            _shouldResetDisplay = true;
          });
          return;
        }
        result = _firstOperand / secondOperand;
        break;
    }

    setState(() {
      _expression =
          '${_formatNumber(_firstOperand)} $_operator ${_formatNumber(secondOperand)} =';
      _display = _formatNumber(result);
      _operator = '';
      _shouldResetDisplay = true;
    });
  }

  void _onEqualsPressed() {
    _calculate();
  }

  void _onClearPressed() {
    setState(() {
      _display = '0';
      _expression = '';
      _firstOperand = 0;
      _operator = '';
      _shouldResetDisplay = false;
    });
  }

  void _onToggleSign() {
    setState(() {
      if (_display != '0' && _display != 'Error') {
        if (_display.startsWith('-')) {
          _display = _display.substring(1);
        } else {
          _display = '-$_display';
        }
      }
    });
  }

  void _onPercentPressed() {
    if (_display == 'Error') return;
    setState(() {
      final value = double.parse(_display);
      _display = _formatNumber(value / 100);
    });
  }

  String _formatNumber(double value) {
    if (value == value.toInt().toDouble()) {
      return value.toInt().toString();
    }
    final formatted = value.toStringAsFixed(8);
    return formatted.replaceAll(RegExp(r'0+$'), '').replaceAll(RegExp(r'\.$'), '');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                alignment: Alignment.bottomRight,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      _expression,
                      style: const TextStyle(
                        fontSize: 20,
                        color: Colors.white54,
                      ),
                    ),
                    const SizedBox(height: 8),
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      alignment: Alignment.centerRight,
                      child: Text(
                        _display,
                        style: const TextStyle(
                          fontSize: 64,
                          fontWeight: FontWeight.w300,
                          color: Colors.white,
                        ),
                        maxLines: 1,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: [
                  _buildButtonRow([
                    _ButtonData('AC', _onClearPressed, type: _ButtonType.function),
                    _ButtonData('+/−', () => _onToggleSign(), type: _ButtonType.function),
                    _ButtonData('%', () => _onPercentPressed(), type: _ButtonType.function),
                    _ButtonData('÷', () => _onOperatorPressed('÷'), type: _ButtonType.operator),
                  ]),
                  const SizedBox(height: 12),
                  _buildButtonRow([
                    _ButtonData('7', () => _onDigitPressed('7')),
                    _ButtonData('8', () => _onDigitPressed('8')),
                    _ButtonData('9', () => _onDigitPressed('9')),
                    _ButtonData('×', () => _onOperatorPressed('×'), type: _ButtonType.operator),
                  ]),
                  const SizedBox(height: 12),
                  _buildButtonRow([
                    _ButtonData('4', () => _onDigitPressed('4')),
                    _ButtonData('5', () => _onDigitPressed('5')),
                    _ButtonData('6', () => _onDigitPressed('6')),
                    _ButtonData('−', () => _onOperatorPressed('−'), type: _ButtonType.operator),
                  ]),
                  const SizedBox(height: 12),
                  _buildButtonRow([
                    _ButtonData('1', () => _onDigitPressed('1')),
                    _ButtonData('2', () => _onDigitPressed('2')),
                    _ButtonData('3', () => _onDigitPressed('3')),
                    _ButtonData('+', () => _onOperatorPressed('+'), type: _ButtonType.operator),
                  ]),
                  const SizedBox(height: 12),
                  _buildButtonRow([
                    _ButtonData('0', () => _onDigitPressed('0'), flex: 2),
                    _ButtonData('.', () => _onDecimalPressed()),
                    _ButtonData('=', () => _onEqualsPressed(), type: _ButtonType.operator),
                  ]),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildButtonRow(List<_ButtonData> buttons) {
    return Row(
      children: buttons.map((btn) {
        return Expanded(
          flex: btn.flex,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 6),
            child: _CalcButton(
              label: btn.label,
              onPressed: btn.onPressed,
              type: btn.type,
            ),
          ),
        );
      }).toList(),
    );
  }
}

enum _ButtonType { digit, operator, function }

class _ButtonData {
  final String label;
  final VoidCallback onPressed;
  final _ButtonType type;
  final int flex;

  _ButtonData(this.label, this.onPressed, {this.type = _ButtonType.digit, this.flex = 1});
}

class _CalcButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final _ButtonType type;

  const _CalcButton({
    required this.label,
    required this.onPressed,
    this.type = _ButtonType.digit,
  });

  Color get _backgroundColor {
    switch (type) {
      case _ButtonType.operator:
        return const Color(0xFFFF9F0A);
      case _ButtonType.function:
        return const Color(0xFF505050);
      case _ButtonType.digit:
        return const Color(0xFF333333);
    }
  }

  Color get _textColor {
    switch (type) {
      case _ButtonType.operator:
        return Colors.white;
      case _ButtonType.function:
        return Colors.white;
      case _ButtonType.digit:
        return Colors.white;
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 72,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: _backgroundColor,
          foregroundColor: _textColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(36),
          ),
          elevation: 0,
          textStyle: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w400,
          ),
        ),
        child: Text(label),
      ),
    );
  }
}
