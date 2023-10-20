//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: Basic button control
//
// $NoKeywords: $
//=============================================================================//

#include <stdio.h>
#include <utlsymbol.h>

#include <vgui/IBorder.h>
#include <vgui/IInput.h>
#include <vgui/IScheme.h>
#include <vgui/ISurface.h>
#include <vgui/ISystem.h>
#include <vgui/IVGui.h>
#include <vgui/MouseCode.h>
#include <vgui/KeyCode.h>
#include <KeyValues.h>

#include <vgui_controls/Button.h>
#include <vgui_controls/FocusNavGroup.h>

// memdbgon must be the last include file in a .cpp file!!!
#include <tier0/memdbgon.h>

using namespace vgui;

// global list of all the names of all the sounds played by buttons
CUtlSymbolTable g_ButtonSoundNames;

DECLARE_BUILD_FACTORY_DEFAULT_TEXT( Button, Button );

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
Button::Button(Panel *parent, const char *panelName, const char *text, Panel *pActionSignalTarget, const char *pCmd ) : Label(parent, panelName, text)
{
	Init();
	if ( pActionSignalTarget && pCmd )
	{
		AddActionSignalTarget( pActionSignalTarget );
		SetCommand( pCmd );
	}
}

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
Button::Button(Panel *parent, const char *panelName, const wchar_t *wszText, Panel *pActionSignalTarget, const char *pCmd ) : Label(parent, panelName, wszText)
{
	Init();
	if ( pActionSignalTarget && pCmd )
	{
		AddActionSignalTarget( pActionSignalTarget );
		SetCommand( pCmd );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::Init()
{
	_buttonFlags.SetFlag( USE_CAPTURE_MOUSE | BUTTON_BORDER_ENABLED );

	_mouseClickMask = 0;
	_actionMessage = NULL;
	_defaultBorder = NULL;
	_depressedBorder = NULL;
	_keyFocusBorder = NULL;
	m_bSelectionStateSaved = false;
	m_bStaySelectedOnClick = false;
	m_sArmedSoundName = UTL_INVAL_SYMBOL;
	m_sDepressedSoundName = UTL_INVAL_SYMBOL;
	m_sReleasedSoundName = UTL_INVAL_SYMBOL;
	SetTextInset(6, 0);
	SetMouseClickEnabled( MOUSE_LEFT, true );
	SetButtonActivationType(ACTIVATE_ONPRESSEDANDRELEASED);

	// labels have this off by default, but we need it on
	SetPaintBackgroundEnabled( true );

	_paint = true;

	REGISTER_COLOR_AS_OVERRIDABLE( _defaultFgColor, "defaultFgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _defaultBgColor, "defaultBgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _armedFgColor, "armedFgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _armedBgColor, "armedBgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _depressedFgColor, "depressedFgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _depressedBgColor, "depressedBgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _selectedFgColor, "selectedFgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _selectedBgColor, "selectedBgColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _keyboardFocusColor, "keyboardFocusColor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _blinkFgColor, "blinkFgColor_override" );
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
Button::~Button()
{
	if (_actionMessage)
	{
		_actionMessage->deleteThis();
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::SetButtonActivationType(ActivationType_t activationType)
{
	_activationType = activationType;
}

//-----------------------------------------------------------------------------
// Purpose: Set button border attribute enabled.
//-----------------------------------------------------------------------------
void Button::SetButtonBorderEnabled( bool state )
{
	if ( state != _buttonFlags.IsFlagSet( BUTTON_BORDER_ENABLED ) )
	{
		_buttonFlags.SetFlag( BUTTON_BORDER_ENABLED, state );
		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose:	Set button selected state.
//-----------------------------------------------------------------------------
void Button::SetSelected( bool state )
{
	if ( _buttonFlags.IsFlagSet( SELECTED ) != state )
	{
		_buttonFlags.SetFlag( SELECTED, state );
		RecalculateDepressedState();
		InvalidateLayout(false);
	}

	if ( state && _buttonFlags.IsFlagSet( ARMED ) )
	{
		_buttonFlags.SetFlag( ARMED,  false );
		InvalidateLayout(false);
	}
}

void Button::SetBlink( bool state )
{
	if ( _buttonFlags.IsFlagSet( BLINK ) != state )
	{
		_buttonFlags.SetFlag( BLINK, state );
		RecalculateDepressedState();
		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose:	Set button force depressed state.
//-----------------------------------------------------------------------------
void Button::ForceDepressed(bool state)
{
	if ( _buttonFlags.IsFlagSet( FORCE_DEPRESSED ) != state )
	{
		_buttonFlags.SetFlag( FORCE_DEPRESSED, state );
		RecalculateDepressedState();
		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose:	Set button depressed state with respect to the force depressed state.
//-----------------------------------------------------------------------------
void Button::RecalculateDepressedState( void )
{
	bool newState;
	if (!IsEnabled())
	{
		newState = false;
	}
	else
	{
		if ( m_bStaySelectedOnClick && _buttonFlags.IsFlagSet( SELECTED ) )
		{
			newState = false;
		}
		else
		{
			newState = _buttonFlags.IsFlagSet( FORCE_DEPRESSED ) ? true : (_buttonFlags.IsFlagSet(ARMED) && _buttonFlags.IsFlagSet( SELECTED ) );
		}
	}

	_buttonFlags.SetFlag( DEPRESSED, newState );
}

//-----------------------------------------------------------------------------
// Purpose: Sets whether or not the button captures all mouse input when depressed
//			Defaults to true
//			Should be set to false for things like menu items where there is a higher-level mouse capture
//-----------------------------------------------------------------------------
void Button::SetUseCaptureMouse( bool state )
{
	_buttonFlags.SetFlag( USE_CAPTURE_MOUSE, state );
}

//-----------------------------------------------------------------------------
// Purpose: Check if mouse capture is enabled.
// Output : Returns true on success, false on failure.
//-----------------------------------------------------------------------------
bool Button::IsUseCaptureMouseEnabled( void )
{
	return _buttonFlags.IsFlagSet( USE_CAPTURE_MOUSE );
}

//-----------------------------------------------------------------------------
// Purpose:	Set armed state.
//-----------------------------------------------------------------------------
void Button::SetArmed(bool state)
{
	if ( _buttonFlags.IsFlagSet( ARMED ) != state )
	{
		_buttonFlags.SetFlag( ARMED, state );
		RecalculateDepressedState();
		InvalidateLayout(false);

		// play any sounds specified
		if (state && m_sArmedSoundName != UTL_INVAL_SYMBOL)
		{
			surface()->PlaySound(g_ButtonSoundNames.String(m_sArmedSoundName));
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose:	Check armed state
//-----------------------------------------------------------------------------
bool Button::IsArmed()
{
	return _buttonFlags.IsFlagSet( ARMED );
}


KeyValues *Button::GetActionMessage()
{
	return _actionMessage->MakeCopy();
}

void Button::PlayButtonReleasedSound()
{
	// check for playing a transition sound
	if ( m_sReleasedSoundName != UTL_INVAL_SYMBOL )
	{
		surface()->PlaySound( g_ButtonSoundNames.String( m_sReleasedSoundName ) );
	}
}

//-----------------------------------------------------------------------------
// Purpose:	Activate a button click.
//-----------------------------------------------------------------------------
void Button::DoClick()
{
	SetSelected(true);
	FireActionSignal();
	PlayButtonReleasedSound();

	static ConVarRef vgui_nav_lock( "vgui_nav_lock" );
	if ( ( !vgui_nav_lock.IsValid() || vgui_nav_lock.GetInt() == 0 ) && NavigateActivate() )
	{
		vgui_nav_lock.SetValue( 1 );
	}

	if ( !m_bStaySelectedOnClick )
	{
		SetSelected(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Check selected state
//-----------------------------------------------------------------------------
bool Button::IsSelected()
{
	return _buttonFlags.IsFlagSet( SELECTED );
}

//-----------------------------------------------------------------------------
// Purpose:	Check depressed state
//-----------------------------------------------------------------------------
bool Button::IsDepressed()
{
	return _buttonFlags.IsFlagSet( DEPRESSED );
}

bool Button::IsBlinking( void )
{
	return _buttonFlags.IsFlagSet( BLINK );
}


//-----------------------------------------------------------------------------
// Drawing focus box?
//-----------------------------------------------------------------------------
bool Button::IsDrawingFocusBox()
{
	return _buttonFlags.IsFlagSet( DRAW_FOCUS_BOX );
}

void Button::DrawFocusBox( bool bEnable )
{
	_buttonFlags.SetFlag( DRAW_FOCUS_BOX, bEnable );
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void Button::NavigateTo()
{
	BaseClass::NavigateTo();

	SetArmed( true );

	if ( IsPC() )
	{
		RequestFocus( 0 );
	}
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void Button::NavigateFrom()
{
	BaseClass::NavigateFrom();

	SetArmed( false );

	OnKeyCodeReleased( KEY_XBUTTON_A );
}
	
//-----------------------------------------------------------------------------
// Purpose:	Paint button on screen
//-----------------------------------------------------------------------------
void Button::Paint(void)
{
	if ( !ShouldPaint() )
		return; 

	BaseClass::Paint();

	if ( HasFocus() && IsEnabled() && IsDrawingFocusBox() )
	{
		int x0, y0, x1, y1;
		int wide, tall;
		GetSize(wide, tall);
		x0 = 3, y0 = 3, x1 = wide - 4 , y1 = tall - 2;
		DrawFocusBorder(x0, y0, x1, y1);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Perform graphical layout of button.
//-----------------------------------------------------------------------------
void Button::PerformLayout()
{
	// reset our border
	SetBorder( GetBorder(_buttonFlags.IsFlagSet( DEPRESSED ), _buttonFlags.IsFlagSet( ARMED ), _buttonFlags.IsFlagSet( SELECTED ), HasFocus() ) );

	// set our color
	SetFgColor(GetButtonFgColor());
	SetBgColor(GetButtonBgColor());

	BaseClass::PerformLayout();
}

//-----------------------------------------------------------------------------
// Purpose: Get button foreground color
// Output : Color
//-----------------------------------------------------------------------------
Color Button::GetButtonFgColor()
{
	if ( !_buttonFlags.IsFlagSet( BLINK ) )
	{
		if (_buttonFlags.IsFlagSet( DEPRESSED ))
			return _depressedFgColor;
		if (_buttonFlags.IsFlagSet( ARMED ))
			return _armedFgColor;
		if (_buttonFlags.IsFlagSet( SELECTED))
			return _selectedFgColor;
		return _defaultFgColor;
	}

	Color cBlendedColor;

	if (_buttonFlags.IsFlagSet( DEPRESSED ))
		cBlendedColor = _depressedFgColor;
	else if (_buttonFlags.IsFlagSet( ARMED ))
		cBlendedColor = _armedFgColor;
	else if (_buttonFlags.IsFlagSet( SELECTED ))
		cBlendedColor = _selectedFgColor;
	else
		cBlendedColor = _defaultFgColor;

	float fBlink = ( sinf( system()->GetTimeMillis() * 0.01f ) + 1.0f ) * 0.5f;

	if ( _buttonFlags.IsFlagSet( BLINK ) )
	{
		cBlendedColor[ 0 ] = (float)cBlendedColor[ 0 ] * fBlink + (float)_blinkFgColor[ 0 ] * ( 1.0f - fBlink );
		cBlendedColor[ 1 ] = (float)cBlendedColor[ 1 ] * fBlink + (float)_blinkFgColor[ 1 ] * ( 1.0f - fBlink );
		cBlendedColor[ 2 ] = (float)cBlendedColor[ 2 ] * fBlink + (float)_blinkFgColor[ 2 ] * ( 1.0f - fBlink );
		cBlendedColor[ 3 ] = (float)cBlendedColor[ 3 ] * fBlink + (float)_blinkFgColor[ 3 ] * ( 1.0f - fBlink );
	}

	return cBlendedColor;
}

//-----------------------------------------------------------------------------
// Purpose: Get button background color
//-----------------------------------------------------------------------------
Color Button::GetButtonBgColor()
{
	if (_buttonFlags.IsFlagSet( DEPRESSED ))
		return _depressedBgColor;
	if (_buttonFlags.IsFlagSet( ARMED ))
		return _armedBgColor;
	if (_buttonFlags.IsFlagSet( SELECTED ))
		return _selectedBgColor;
	return _defaultBgColor;
}

//-----------------------------------------------------------------------------
// Purpose: Called when key focus is received
//-----------------------------------------------------------------------------
void Button::OnSetFocus()
{
	InvalidateLayout(false);
	BaseClass::OnSetFocus();
}

//-----------------------------------------------------------------------------
// Purpose: Respond when focus is killed
//-----------------------------------------------------------------------------
void Button::OnKillFocus()
{
	InvalidateLayout(false);
	BaseClass::OnKillFocus();
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::ApplySchemeSettings(IScheme *pScheme)
{
	BaseClass::ApplySchemeSettings(pScheme);

	// get the borders we need
	_defaultBorder = pScheme->GetBorder("ButtonBorder");
	_depressedBorder = pScheme->GetBorder("ButtonDepressedBorder");
	_keyFocusBorder = pScheme->GetBorder("ButtonKeyFocusBorder");

	_defaultFgColor = GetSchemeColor("Button.TextColor", Color(255, 255, 255, 255), pScheme);
	_defaultBgColor = GetSchemeColor("Button.BgColor", Color(0, 0, 0, 255), pScheme);

	_armedFgColor = GetSchemeColor("Button.ArmedTextColor", _defaultFgColor, pScheme);
	_armedBgColor = GetSchemeColor("Button.ArmedBgColor", _defaultBgColor, pScheme);

	_selectedFgColor = GetSchemeColor("Button.SelectedTextColor", _selectedFgColor, pScheme);
	_selectedBgColor = GetSchemeColor("Button.SelectedBgColor", _selectedBgColor, pScheme);

	_depressedFgColor = GetSchemeColor("Button.DepressedTextColor", _defaultFgColor, pScheme);
	_depressedBgColor = GetSchemeColor("Button.DepressedBgColor", _defaultBgColor, pScheme);
	_keyboardFocusColor = GetSchemeColor("Button.FocusBorderColor", Color(0,0,0,255), pScheme);

	_blinkFgColor = GetSchemeColor("Button.BlinkColor", Color(255, 155, 0, 255), pScheme);
	InvalidateLayout();
}

//-----------------------------------------------------------------------------
// Purpose: Set default button colors.
//-----------------------------------------------------------------------------
void Button::SetDefaultColor(Color fgColor, Color bgColor)
{
	if (!(_defaultFgColor == fgColor && _defaultBgColor == bgColor))
	{
		_defaultFgColor = fgColor;
		_defaultBgColor = bgColor;

		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set armed button colors
//-----------------------------------------------------------------------------
void Button::SetArmedColor(Color fgColor, Color bgColor)
{
	if (!(_armedFgColor == fgColor && _armedBgColor == bgColor))
	{
		_armedFgColor = fgColor;
		_armedBgColor = bgColor;

		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set armed button colors
//-----------------------------------------------------------------------------
void Button::SetSelectedColor(Color fgColor, Color bgColor)
{
	if (!(_selectedFgColor == fgColor && _selectedBgColor == bgColor))
	{
		_selectedFgColor = fgColor;
		_selectedBgColor = bgColor;

		InvalidateLayout(false);
	}
}
//-----------------------------------------------------------------------------
// Purpose: Set depressed button colors
//-----------------------------------------------------------------------------
void Button::SetDepressedColor(Color fgColor, Color bgColor)
{
	if (!(_depressedFgColor == fgColor && _depressedBgColor == bgColor))
	{
		_depressedFgColor = fgColor;
		_depressedBgColor = bgColor;

		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set blink button color
//-----------------------------------------------------------------------------
void Button::SetBlinkColor(Color fgColor)
{
	if (!(_blinkFgColor == fgColor))
	{
		_blinkFgColor = fgColor;

		InvalidateLayout(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set default button border attributes.
//-----------------------------------------------------------------------------
void Button::SetDefaultBorder(IBorder *border)
{
	_defaultBorder = border;
	InvalidateLayout(false);
}

//-----------------------------------------------------------------------------
// Purpose: Set depressed button border attributes.
//-----------------------------------------------------------------------------
void Button::SetDepressedBorder(IBorder *border)
{
	_depressedBorder = border;
	InvalidateLayout(false);
}

//-----------------------------------------------------------------------------
// Purpose: Set key focus button border attributes.
//-----------------------------------------------------------------------------
void Button::SetKeyFocusBorder(IBorder *border)
{
	_keyFocusBorder = border;
	InvalidateLayout(false);
}


//-----------------------------------------------------------------------------
// Purpose: Get button border attributes.
//-----------------------------------------------------------------------------
IBorder *Button::GetBorder(bool depressed, bool armed, bool selected, bool keyfocus)
{
	if ( _buttonFlags.IsFlagSet( BUTTON_BORDER_ENABLED ) )
	{
		// raised buttons with no armed state
		if (depressed)
			return _depressedBorder;
		if (keyfocus)
			return _keyFocusBorder;
		if (IsEnabled() && _buttonFlags.IsFlagSet( DEFAULT_BUTTON ))
			return _keyFocusBorder;
		return _defaultBorder;
	}
	else
	{
		// flat buttons that raise
		if (depressed)
			return _depressedBorder;
		if (armed)
			return _defaultBorder;
	}

	return _defaultBorder;
}

//-----------------------------------------------------------------------------
// Purpose: sets this button to be the button that is accessed by default 
//			when the user hits ENTER or SPACE
//-----------------------------------------------------------------------------
void Button::SetAsCurrentDefaultButton(int state)
{
	if ( _buttonFlags.IsFlagSet( DEFAULT_BUTTON ) != (bool)state )
	{
		_buttonFlags.SetFlag( DEFAULT_BUTTON, state );
		if (state)
		{
			// post a message up notifying our nav group that we're now the default button
			KeyValues *msg = new KeyValues( "CurrentDefaultButtonSet" );
			msg->SetInt( "button", ToHandle() );
			CallParentFunction( msg );
		}

		InvalidateLayout();
		Repaint();
	}
}

//-----------------------------------------------------------------------------
// Purpose: sets this button to be the button that is accessed by default 
//			when the user hits ENTER or SPACE
//-----------------------------------------------------------------------------
void Button::SetAsDefaultButton(int state)
{
	if ( _buttonFlags.IsFlagSet( DEFAULT_BUTTON ) != (bool)state )
	{
		_buttonFlags.SetFlag( DEFAULT_BUTTON, state );
		if (state)
		{
			// post a message up notifying our nav group that we're now the default button
			KeyValues *msg = new KeyValues( "DefaultButtonSet" );
			msg->SetInt( "button", ToHandle() );
			CallParentFunction( msg );
		}

		InvalidateLayout();
		Repaint();
	}
}

//-----------------------------------------------------------------------------
// Purpose: sets rollover sound
//-----------------------------------------------------------------------------
void Button::SetArmedSound(const char *sound)
{
	if (sound)
	{
		m_sArmedSoundName = g_ButtonSoundNames.AddString(sound);
	}
	else
	{
		m_sArmedSoundName = UTL_INVAL_SYMBOL;
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::SetDepressedSound(const char *sound)
{
	if (sound)
	{
		m_sDepressedSoundName = g_ButtonSoundNames.AddString(sound);
	}
	else
	{
		m_sDepressedSoundName = UTL_INVAL_SYMBOL;
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::SetReleasedSound(const char *sound)
{
	if (sound)
	{
		m_sReleasedSoundName = g_ButtonSoundNames.AddString(sound);
	}
	else
	{
		m_sReleasedSoundName = UTL_INVAL_SYMBOL;
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set button to be mouse clickable or not.
//-----------------------------------------------------------------------------
void Button::SetMouseClickEnabled(MouseCode code,bool state)
{
	if(state)
	{
		//set bit to 1
		_mouseClickMask|=1<<((int)(code+1));
	}
	else
	{
		//set bit to 0
		_mouseClickMask&=~(1<<((int)(code+1)));
	}	
}

//-----------------------------------------------------------------------------
// Purpose: Check if button is mouse clickable
//-----------------------------------------------------------------------------
bool Button::IsMouseClickEnabled(MouseCode code)
{
	if(_mouseClickMask&(1<<((int)(code+1))))
	{
		return true;
	}
	return false;
}

//-----------------------------------------------------------------------------
// Purpose: sets the command to send when the button is pressed
//-----------------------------------------------------------------------------
void Button::SetCommand( const char *command )
{
	SetCommand(new KeyValues("Command", "command", command));
}

//-----------------------------------------------------------------------------
// Purpose: sets the message to send when the button is pressed
//-----------------------------------------------------------------------------
void Button::SetCommand( KeyValues *message )
{
	// delete the old message
	if (_actionMessage)
	{
		_actionMessage->deleteThis();
	}

	_actionMessage = message;
}

//-----------------------------------------------------------------------------
// Purpose: Peeks at the message to send when button is pressed
// Input  :  - 
// Output : KeyValues
//-----------------------------------------------------------------------------
KeyValues *Button::GetCommand()
{
	return _actionMessage;
}

//-----------------------------------------------------------------------------
// Purpose: Message targets that the button has been pressed
//-----------------------------------------------------------------------------
void Button::FireActionSignal()
{
	// message-based action signal
	if (_actionMessage)
	{
		// see if it's a url
		if (!stricmp(_actionMessage->GetName(), "command")
			&& !strnicmp(_actionMessage->GetString("command", ""), "url ", strlen("url "))
			&& strstr(_actionMessage->GetString("command", ""), "://"))
		{
			// it's a command to launch a url, run it
			system()->ShellExecute("open", _actionMessage->GetString("command", "      ") + 4);
		}
		PostActionSignal(_actionMessage->MakeCopy());
	}
}

//-----------------------------------------------------------------------------
// Purpose: gets info about the button
//-----------------------------------------------------------------------------
bool Button::RequestInfo(KeyValues *outputData)
{
	if (!stricmp(outputData->GetName(), "CanBeDefaultButton"))
	{
		outputData->SetInt("result", CanBeDefaultButton() ? 1 : 0);
		return true;
	}
	else if (!stricmp(outputData->GetName(), "GetState"))
	{
		outputData->SetInt("state", IsSelected());
		return true;
	}
	else if ( !stricmp( outputData->GetName(), "GetCommand" ))
	{
		if ( _actionMessage )
		{
			outputData->SetString( "command", _actionMessage->GetString( "command", "" ) );
		}
		else
		{
			outputData->SetString( "command", "" );
		}
		return true;
	}


	return BaseClass::RequestInfo(outputData);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
bool Button::CanBeDefaultButton(void)
{
    return true;
}


//-----------------------------------------------------------------------------
// Purpose: Get control settings for editing
//-----------------------------------------------------------------------------
void Button::GetSettings( KeyValues *outResourceData )
{
	BaseClass::GetSettings(outResourceData);

	if (_actionMessage)
	{
		outResourceData->SetString("command", _actionMessage->GetString("command", ""));
	}
	outResourceData->SetInt("default", _buttonFlags.IsFlagSet( DEFAULT_BUTTON ) );
	if ( m_bSelectionStateSaved )
	{
		outResourceData->SetInt( "selected", IsSelected() );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::ApplySettings( KeyValues *inResourceData )
{
	BaseClass::ApplySettings(inResourceData);

	const char *cmd = inResourceData->GetString("command", "");
	if (*cmd)
	{
		// add in the command
		SetCommand(cmd);
	}

	// set default button state
	int defaultButton = inResourceData->GetInt("default");
	if (defaultButton && CanBeDefaultButton())
	{
		SetAsDefaultButton(true);
	}

	// saved selection state
	int iSelected = inResourceData->GetInt( "selected", -1 );
	if ( iSelected != -1 )
	{
		SetSelected( iSelected != 0 );
		m_bSelectionStateSaved = true;
	}

	m_bStaySelectedOnClick = inResourceData->GetBool( "stayselectedonclick", false );

	const char *sound = inResourceData->GetString("sound_armed", "");
	if (*sound)
	{
		SetArmedSound(sound);
	}
	sound = inResourceData->GetString("sound_depressed", "");
	if (*sound)
	{
		SetDepressedSound(sound);
	}
	sound = inResourceData->GetString("sound_released", "");
	if (*sound)
	{
		SetReleasedSound(sound);
	}

	_activationType = (ActivationType_t)inResourceData->GetInt( "button_activation_type", ACTIVATE_ONRELEASED );
}


//-----------------------------------------------------------------------------
// Purpose: Describes editing details
//-----------------------------------------------------------------------------
const char *Button::GetDescription( void )
{
	static char buf[1024];
	Q_snprintf(buf, sizeof(buf), "%s, string command, int default", BaseClass::GetDescription());
	return buf;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnSetState(int state)
{
	SetSelected((bool)state);
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnCursorEntered()
{
	if (IsEnabled() && !IsSelected() )
	{
		SetArmed( true );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnCursorExited()
{
	if ( !_buttonFlags.IsFlagSet( BUTTON_KEY_DOWN ) && !IsSelected() )
	{
		SetArmed( false );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnMousePressed(MouseCode code)
{
	if (!IsEnabled())
		return;
	
	if (!IsMouseClickEnabled(code))
		return;

	if (_activationType == ACTIVATE_ONPRESSED)
	{
		if ( IsKeyBoardInputEnabled() )
		{
			RequestFocus();
		}
		DoClick();
		return;
	}

	// play activation sound
	if (m_sDepressedSoundName != UTL_INVAL_SYMBOL)
	{
		surface()->PlaySound(g_ButtonSoundNames.String(m_sDepressedSoundName));
	}

	if (IsUseCaptureMouseEnabled() && _activationType == ACTIVATE_ONPRESSEDANDRELEASED)
	{
		{
			if ( IsKeyBoardInputEnabled() )
			{
				RequestFocus();
			}
			SetSelected(true);
			Repaint();
		}

		// lock mouse input to going to this button
		input()->SetMouseCapture(GetVPanel());
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnMouseDoublePressed(MouseCode code)
{
	OnMousePressed(code);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnMouseReleased(MouseCode code)
{
	// ensure mouse capture gets released
	if (IsUseCaptureMouseEnabled())
	{
		input()->SetMouseCapture(NULL);
	}

	if (_activationType == ACTIVATE_ONPRESSED)
		return;

	if (!IsMouseClickEnabled(code))
		return;

	if (!IsSelected() && _activationType == ACTIVATE_ONPRESSEDANDRELEASED)
		return;

	// it has to be both enabled and (mouse over the button or using a key) to fire
	if ( IsEnabled() && ( GetVPanel() == input()->GetMouseOver() || _buttonFlags.IsFlagSet( BUTTON_KEY_DOWN ) ) )
	{
		DoClick();
	}
	else if ( !m_bStaySelectedOnClick )
	{
		SetSelected(false);
	}

	// make sure the button gets unselected
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnKeyCodePressed(KeyCode code)
{
	KeyCode localCode = GetBaseButtonCode( code );

	if( ( localCode == KEY_XBUTTON_A ) && IsEnabled() )
	{
		SetArmed( true );
		_buttonFlags.SetFlag( BUTTON_KEY_DOWN );
		if( _activationType != ACTIVATE_ONRELEASED )
		{
			DoClick();
		}
	}
	else if (code == KEY_SPACE || code == KEY_ENTER)
	{
		SetArmed(true);
		_buttonFlags.SetFlag( BUTTON_KEY_DOWN );
		OnMousePressed(MOUSE_LEFT);
		if (IsUseCaptureMouseEnabled()) // undo the mouse capture since its a fake mouse click!
		{
			input()->SetMouseCapture(NULL);
		}
	}
	else
	{
		_buttonFlags.ClearFlag( BUTTON_KEY_DOWN );
		BaseClass::OnKeyCodePressed( code );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Button::OnKeyCodeReleased( KeyCode keycode )
{
	vgui::KeyCode code = GetBaseButtonCode( keycode );

	if ( _buttonFlags.IsFlagSet( BUTTON_KEY_DOWN ) && ( code == KEY_XBUTTON_A || code == KEY_XBUTTON_START ) )
	{
		SetArmed( true );
		if( _activationType != ACTIVATE_ONPRESSED )
		{
			DoClick();
		}
	}
	else if (_buttonFlags.IsFlagSet( BUTTON_KEY_DOWN ) && (code == KEY_SPACE || code == KEY_ENTER))
	{
		SetArmed(true);
		OnMouseReleased(MOUSE_LEFT);
	}
	else
	{
		BaseClass::OnKeyCodeReleased( keycode );
	}
	_buttonFlags.ClearFlag( BUTTON_KEY_DOWN );

	if ( !( code == KEY_XSTICK1_UP || code == KEY_XSTICK1_DOWN || code == KEY_XSTICK1_LEFT || code == KEY_XSTICK1_RIGHT || 
			code == KEY_XSTICK2_UP || code == KEY_XSTICK2_DOWN || code == KEY_XSTICK2_LEFT || code == KEY_XSTICK2_RIGHT || 
			code == KEY_XBUTTON_UP || code == KEY_XBUTTON_DOWN || code == KEY_XBUTTON_LEFT || code == KEY_XBUTTON_RIGHT || 
			keycode == KEY_UP|| keycode == KEY_DOWN || keycode == KEY_LEFT || keycode == KEY_RIGHT ) )
	{
		SetArmed( false );
	}
}

//-----------------------------------------------------------------------------
// Purpose: Override this to draw different focus border
//-----------------------------------------------------------------------------
void Button::DrawFocusBorder(int tx0, int ty0, int tx1, int ty1)
{
	surface()->DrawSetColor(_keyboardFocusColor);
	DrawDashedLine(tx0, ty0, tx1, ty0+1, 1, 1);		// top
	DrawDashedLine(tx0, ty0, tx0+1, ty1, 1, 1);		// left
	DrawDashedLine(tx0, ty1-1, tx1, ty1, 1, 1);		// bottom
	DrawDashedLine(tx1-1, ty0, tx1, ty1, 1, 1);		// right
}

//-----------------------------------------------------------------------------
// Purpose: Size the object to its button and text.  - only works from in ApplySchemeSettings or PerformLayout()
//-----------------------------------------------------------------------------
void Button::SizeToContents()
{
	int wide, tall;
	GetContentSize(wide, tall);
	SetSize(wide + Label::Content, tall + Label::Content);
}

//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: 
//
// $NoKeywords: $
//===========================================================================//

#include <assert.h>
#include <math.h> // for ceil()
#define PROTECTED_THINGS_DISABLE

#include "tier1/utlstring.h"
#include "vgui/Cursor.h"
#include "vgui/MouseCode.h"
#include "vgui/IBorder.h"
#include "vgui/IInput.h"
#include "vgui/ILocalize.h"
#include "vgui/IPanel.h"
#include "vgui/ISurface.h"
#include "vgui/IScheme.h"
#include "vgui/KeyCode.h"

#include "vgui_controls/AnimationController.h"
#include "vgui_controls/Controls.h"
#include "vgui_controls/Frame.h"
#include "vgui_controls/Button.h"
#include "vgui_controls/Menu.h"
#include "vgui_controls/MenuButton.h"
#include "vgui_controls/TextImage.h"

#include "KeyValues.h"

#include <stdio.h>

// memdbgon must be the last include file in a .cpp file!!!
#include "tier0/memdbgon.h"

using namespace vgui;

static const int DEFAULT_SNAP_RANGE = 10; // number of pixels distance before the frame will snap to an edge
static const int CAPTION_TITLE_BORDER = 7;
static const int CAPTION_TITLE_BORDER_SMALL = 0;

namespace
{
	//-----------------------------------------------------------------------------
	// Purpose: Invisible panel to handle dragging/resizing frames
	//-----------------------------------------------------------------------------
	class GripPanel : public Panel
	{
	public:
		GripPanel(Frame *dragFrame, const char *name, int xdir, int ydir) : Panel(dragFrame, name)
		{
			_frame = dragFrame;
			_dragging = false;
			_dragMultX = xdir;
			_dragMultY = ydir;
			SetPaintEnabled(false);
			SetPaintBackgroundEnabled(false);
			SetPaintBorderEnabled(false);
			m_iSnapRange = DEFAULT_SNAP_RANGE;

			if (xdir == 1 && ydir == 1)
			{
				// bottom-right grip gets an image
				SetPaintEnabled(true);
				SetPaintBackgroundEnabled(true);
			}

			SetBlockDragChaining( true );
		}
		
		// Purpose- handle window resizing
		// Input- dx, dy, the offet of the mouse pointer from where we started dragging
		virtual void moved(int dx, int dy)
		{
			if (!_frame->IsSizeable())
				return;
			
			// Start off with x, y at the coords of where we started to drag
			int newX = _dragOrgPos[0], newY =_dragOrgPos[1];
			// Start off with width and tall equal from window when we started to drag
			int newWide = _dragOrgSize[0], newTall = _dragOrgSize[1];
			
			// get window's minimum size
			int minWide, minTall;
			_frame->GetMinimumSize( minWide, minTall);
			
			// Handle  width resizing
			newWide += (dx * _dragMultX);
			// Handle the position of the corner x position
			if (_dragMultX == -1)
			{
				// only move if we are not at the minimum
				// if we are at min we have to force the proper offset (dx)
				if (newWide < minWide)
				{
					dx=_dragOrgSize[0]-minWide;
				}
				newX += dx;	  // move window to its new position
			}
			
			// Handle height resizing
			newTall += (dy * _dragMultY);
			// Handle position of corner y position
			if (_dragMultY == -1)
			{
				if (newTall < minTall)
				{
					dy=_dragOrgSize[1]-minTall;
				}
				newY += dy;
			}
			
			if ( _frame->GetClipToParent() )
			{
				// If any coordinate is out of range, snap it back
				if ( newX < 0 )
					newX = 0;
				if ( newY < 0 )
					newY = 0;
				
				int sx, sy;
				surface()->GetScreenSize( sx, sy );

				int w, h;
				_frame->GetSize( w, h );
				if ( newX + w > sx )
				{
					newX = sx - w;
				}
				if ( newY + h > sy )
				{
					newY = sy - h;
				}
			}

			// set new position
			_frame->SetPos(newX, newY);
			// set the new size			
			// if window is below min size it will automatically pop to min size
			_frame->SetSize(newWide, newTall);
			_frame->InvalidateLayout();
			_frame->Repaint();
		}
		
		void OnCursorMoved(int x, int y)
		{
			if (!_dragging)
				return;

			if (!input()->IsMouseDown(MOUSE_LEFT))
			{
				// for some reason we're marked as dragging when the mouse is released
				// trigger a release
				OnMouseReleased(MOUSE_LEFT);
				return;
			}

			input()->GetCursorPos(x, y);
			moved((x - _dragStart[0]), ( y - _dragStart[1]));
			_frame->Repaint();
		}
		
		void OnMousePressed(MouseCode code)
		{
			if (code == MOUSE_LEFT)
			{ 
				_dragging=true;
				int x,y;
				input()->GetCursorPos(x,y);
				_dragStart[0]=x;
				_dragStart[1]=y;
				_frame->GetPos(_dragOrgPos[0],_dragOrgPos[1]);
				_frame->GetSize(_dragOrgSize[0],_dragOrgSize[1]);
				input()->SetMouseCapture(GetVPanel());
				
				// if a child doesn't have focus, get it for ourselves
				VPANEL focus = input()->GetFocus();
				if (!focus || !ipanel()->HasParent(focus, _frame->GetVPanel()))
				{
					_frame->RequestFocus();
				}
				_frame->Repaint();
			}
			else
			{
				GetParent()->OnMousePressed(code);
			}
		}

		void OnMouseDoublePressed(MouseCode code)
		{
			GetParent()->OnMouseDoublePressed(code);
		}

		void Paint()
		{
			// draw the grab handle in the bottom right of the frame
			surface()->DrawSetTextFont(_marlettFont);
			surface()->DrawSetTextPos(0, 0);
			
			// thin highlight lines
			surface()->DrawSetTextColor(GetFgColor());
			surface()->DrawUnicodeChar('p'); 
		}

		void PaintBackground()
		{
			// draw the grab handle in the bottom right of the frame
			surface()->DrawSetTextFont(_marlettFont);
			surface()->DrawSetTextPos(0, 0);
			
			// thick shadow lines
			surface()->DrawSetTextColor(GetBgColor());
			surface()->DrawUnicodeChar('o'); 
		}
		
		void OnMouseReleased(MouseCode code)
		{
			_dragging = false;
			input()->SetMouseCapture(NULL);
		}

		void OnMouseCaptureLost()
		{
			Panel::OnMouseCaptureLost();
			_dragging = false;
		}

		void ApplySchemeSettings(IScheme *pScheme)
		{
			Panel::ApplySchemeSettings(pScheme);
			bool isSmall = ((Frame *)GetParent())->IsSmallCaption();

			_marlettFont = pScheme->GetFont( isSmall ? "MarlettSmall" : "Marlett", IsProportional());
			SetFgColor(GetSchemeColor("FrameGrip.Color1", pScheme));
			SetBgColor(GetSchemeColor("FrameGrip.Color2", pScheme));

			const char *snapRange = pScheme->GetResourceString("Frame.AutoSnapRange");
			if (snapRange && *snapRange)
			{
				m_iSnapRange = atoi(snapRange);
			}
		}
		
	protected:
		Frame *_frame;
		int  _dragMultX;
		int  _dragMultY;
		bool _dragging;
		int  _dragOrgPos[2];
		int  _dragOrgSize[2];
		int  _dragStart[2];
		int  m_iSnapRange;
		HFont _marlettFont;
	};
	
	//-----------------------------------------------------------------------------
	// Purpose: Handles caption grip input for moving dialogs around
	//-----------------------------------------------------------------------------
	class CaptionGripPanel : public GripPanel
	{
	public:
		CaptionGripPanel(Frame* frame, const char *name) : GripPanel(frame, name, 0, 0)
		{
		}
		
		void moved(int dx, int dy)
		{
			if (!_frame->IsMoveable())
				return;

			int newX = _dragOrgPos[0] + dx;
			int newY = _dragOrgPos[1] + dy;

			if (m_iSnapRange)
			{
				// first check docking to desktop
				int wx, wy, ww, wt;
				surface()->GetWorkspaceBounds(wx, wy, ww, wt);
				getInsideSnapPosition(wx, wy, ww, wt, newX, newY);

				// now lets check all windows and see if we snap to those
				// root panel
				VPANEL root = surface()->GetEmbeddedPanel();
				// cycle through panels
				// look for panels that are visible and are popups that we can dock to
				for (int i = 0; i < ipanel()->GetChildCount(root); ++i)
				{
					VPANEL child = ipanel()->GetChild(root, i);
					tryToDock (child, newX, newY);
				}
			}

			if ( _frame->GetClipToParent() )
			{
				// If any coordinate is out of range, snap it back
				if ( newX < 0 )
					newX = 0;
				if ( newY < 0 )
					newY = 0;
				
				int sx, sy;
				surface()->GetScreenSize( sx, sy );

				int w, h;
				_frame->GetSize( w, h );
				if ( newX + w > sx )
				{
					newX = sx - w;
				}
				if ( newY + h > sy )
				{
					newY = sy - h;
				}
			}

			_frame->SetPos(newX, newY);

		}
		
		void tryToDock(VPANEL window, int &newX, int & newY)
		{
			// bail if child is this window	
			if ( window == _frame->GetVPanel())
				return;
			
			int cx, cy, cw, ct;
			if ( (ipanel()->IsVisible(window)) && (ipanel()->IsPopup(window)) )
			{
				// position
				ipanel()->GetAbsPos(window, cx, cy);
				// dimensions
				ipanel()->GetSize(window, cw, ct);
				bool snapped = getOutsideSnapPosition (cx, cy, cw, ct, newX, newY);
				if (snapped)
				{ 
					// if we snapped, we're done with this path
					// dont try to snap to kids
					return;
				}
			}

			// check all children
			for (int i = 0; i < ipanel()->GetChildCount(window); ++i)
			{
				VPANEL child = ipanel()->GetChild(window, i);
				tryToDock(child, newX, newY);
			}

		}

		// Purpose: To calculate the windows new x,y position if it snaps
		//          Will snap to the INSIDE of a window (eg desktop sides
		// Input: boundX boundY, position of candidate window we are seeing if we snap to
		//        boundWide, boundTall, width and height of window we are seeing if we snap to
		// Output: snapToX, snapToY new coords for window, unchanged if we dont snap
		// Returns true if we snapped, false if we did not snap.
		bool getInsideSnapPosition(int boundX, int boundY, int boundWide, int boundTall,
			int &snapToX, int &snapToY)
		{
			
			int wide, tall;
			_frame->GetSize(wide, tall);
			Assert (wide > 0);
			Assert (tall > 0);
			
			bool snapped=false;
			if (abs(snapToX - boundX) < m_iSnapRange)
			{
				snapToX = boundX;
				snapped=true;
			}
			else if (abs((snapToX + wide) - (boundX + boundWide)) < m_iSnapRange)
			{
				snapToX = boundX + boundWide - wide;
				snapped=true;
			}

			if (abs(snapToY - boundY) < m_iSnapRange)
			{
				snapToY = boundY;
				snapped=true;
			}
			else if (abs((snapToY + tall) - (boundY + boundTall)) < m_iSnapRange)
			{
				snapToY = boundY + boundTall - tall;
				snapped=true;
			}
			return snapped;
			
		}

		// Purpose: To calculate the windows new x,y position if it snaps
		//          Will snap to the OUTSIDE edges of a window (i.e. will stick peers together
		// Input: left, top, position of candidate window we are seeing if we snap to
		//        boundWide, boundTall, width and height of window we are seeing if we snap to
		// Output: snapToX, snapToY new coords for window, unchanged if we dont snap
		// Returns true if we snapped, false if we did not snap.
		bool getOutsideSnapPosition(int left, int top, int boundWide, int boundTall,
			int &snapToX, int &snapToY)
		{
			Assert (boundWide >= 0);
			Assert (boundTall >= 0);
						
			bool snapped=false;
			
			int right=left+boundWide;
			int bottom=top+boundTall;

			int wide, tall;
			_frame->GetSize(wide, tall);
			Assert (wide > 0);
			Assert (tall > 0);

			// we now see if we are going to be able to snap to a window side, and not
			// just snap to the "open air"
			// want to make it so that if any part of the window can dock to the candidate, it will

			// is this window horizontally snappable to the candidate
			bool horizSnappable=( 
				//  top of window is in range
				((snapToY > top) && (snapToY < bottom)) 
				// bottom of window is in range
				|| ((snapToY+tall > top) && (snapToY+tall < bottom)) 
				// window is just plain bigger than the window we wanna dock to
				|| ((snapToY < top) && (snapToY+tall > bottom)) ); 
			
			
			// is this window vertically snappable to the candidate
			bool vertSnappable=	( 
				 //  left of window is in range
				((snapToX > left) && (snapToX < right))
				//  right of window is in range
				|| ((snapToX+wide > left) && (snapToX+wide < right)) 
				// window is just plain bigger than the window we wanna dock to
				|| ((snapToX < left) && (snapToX+wide > right)) ); 
			
			// if neither, might as well bail
			if ( !(horizSnappable || vertSnappable) )
				return false;

			//if we're within the snap threshold then snap
			if ( (snapToX <= (right+m_iSnapRange)) && 
				(snapToX >= (right-m_iSnapRange)) ) 
			{  
				if (horizSnappable)
				{
					//disallow "open air" snaps
					snapped=true;
					snapToX = right;  
				}
			}
			else if ((snapToX + wide) >= (left-m_iSnapRange) &&
				(snapToX + wide) <= (left+m_iSnapRange)) 
			{
				if (horizSnappable)
				{
					snapped=true;
					snapToX = left-wide;
				}
			}
			
			if ( (snapToY <= (bottom+m_iSnapRange)) &&
				(snapToY >= (bottom-m_iSnapRange)) ) 
			{
				if (vertSnappable)
				{
					snapped=true;
					snapToY = bottom;
				}
			}
			else if ((snapToY + tall) <= (top+m_iSnapRange) &&
				(snapToY + tall) >= (top-m_iSnapRange)) 
			{
				if (vertSnappable)
				{
					snapped=true;
					snapToY = top-tall;
				}
			}
			return snapped;
		}
	};
	
}

namespace vgui
{
	//-----------------------------------------------------------------------------
	// Purpose: overrides normal button drawing to use different colors & borders
	//-----------------------------------------------------------------------------
	class FrameButton : public Button
	{
	private:
		IBorder *_brightBorder, *_depressedBorder, *_disabledBorder;
		Color _enabledFgColor, _enabledBgColor;
		Color _disabledFgColor, _disabledBgColor;
		bool _disabledLook;
	
	public:
	
		static int GetButtonSide( Frame *pFrame )
		{
			if ( pFrame->IsSmallCaption() )
			{
				return 12;
			}

			return 18;
		}
		
		
		FrameButton(Panel *parent, const char *name, const char *text) : Button(parent, name, text)
		{
			SetSize( FrameButton::GetButtonSide( (Frame *)parent ), FrameButton::GetButtonSide( (Frame *)parent ) );
			_brightBorder = NULL;
			_depressedBorder = NULL;
			_disabledBorder = NULL;
			_disabledLook = true;
			SetContentAlignment(Label::a_northwest);
			SetTextInset(2, 1);
			SetBlockDragChaining( true );
		}
		
		virtual void ApplySchemeSettings(IScheme *pScheme)
		{
			Button::ApplySchemeSettings(pScheme);
			
			_enabledFgColor = GetSchemeColor("FrameTitleButton.FgColor", pScheme);
			_enabledBgColor = GetSchemeColor("FrameTitleButton.BgColor", pScheme);

			_disabledFgColor = GetSchemeColor("FrameTitleButton.DisabledFgColor", pScheme);
			_disabledBgColor = GetSchemeColor("FrameTitleButton.DisabledBgColor", pScheme);
			
			_brightBorder = pScheme->GetBorder("TitleButtonBorder");
			_depressedBorder = pScheme->GetBorder("TitleButtonDepressedBorder");
			_disabledBorder = pScheme->GetBorder("TitleButtonDisabledBorder");
			
			SetDisabledLook(_disabledLook);
		}
		
		virtual IBorder *GetBorder(bool depressed, bool armed, bool selected, bool keyfocus)
		{
			if (_disabledLook)
			{
				return _disabledBorder;
			}
			
			if (depressed)
			{
				return _depressedBorder;
			}
			
			return _brightBorder;
		}
		
		virtual void SetDisabledLook(bool state)
		{
			_disabledLook = state;
			if (!_disabledLook)
			{
				SetDefaultColor(_enabledFgColor, _enabledBgColor);
				SetArmedColor(_enabledFgColor, _enabledBgColor);
				SetDepressedColor(_enabledFgColor, _enabledBgColor);
			}
			else
			{
				// setup disabled colors
				SetDefaultColor(_disabledFgColor, _disabledBgColor);
				SetArmedColor(_disabledFgColor, _disabledBgColor);
				SetDepressedColor(_disabledFgColor, _disabledBgColor);
			}
		}

        virtual void PerformLayout()
        {
            Button::PerformLayout();
            Repaint();
        }
		
		// Don't request focus.
		// This will keep items in the listpanel selected.
		virtual void OnMousePressed(MouseCode code)
		{
			if (!IsEnabled())
				return;
			
			if (!IsMouseClickEnabled(code))
				return;
			
			if (IsUseCaptureMouseEnabled())
			{
				{
					SetSelected(true);
					Repaint();
				}
				
				// lock mouse input to going to this button
				input()->SetMouseCapture(GetVPanel());
			}
		}
};


//-----------------------------------------------------------------------------
// Purpose: icon button
//-----------------------------------------------------------------------------
class FrameSystemButton : public MenuButton
{
	DECLARE_CLASS_SIMPLE( FrameSystemButton, MenuButton );

private:
	IImage *_enabled, *_disabled;
	Color _enCol, _disCol;
	bool _respond;
	CUtlString m_EnabledImage;
	CUtlString m_DisabledImage;
	
public:
	FrameSystemButton(Panel *parent, const char *panelName) : MenuButton(parent, panelName, "")
	{
		_disabled = _enabled = NULL;
		_respond = true;
		SetEnabled(false);
		// This menu will open if we use the left or right mouse button
		SetMouseClickEnabled( MOUSE_RIGHT, true );
		SetBlockDragChaining( true );
	}
	
	void SetImages( const char *pEnabledImage, const char *pDisabledImage = NULL )
	{
		m_EnabledImage = pEnabledImage;
		m_DisabledImage = pDisabledImage ? pDisabledImage : pEnabledImage;
	}

	void GetImageSize( int &w, int &h )
	{
		w = h = 0;

		int tw = 0, th = 0;
		if ( _enabled )
		{
			_enabled->GetSize( w, h );
		}
		if ( _disabled )
		{
			_disabled->GetSize( tw, th );
		}
		if ( tw > w )
		{
			w = tw;
		}
		if ( th > h )
		{
			h = th;
		}
	}

	virtual void ApplySchemeSettings(IScheme *pScheme)
	{
		BaseClass::ApplySchemeSettings(pScheme);

		_enCol = GetSchemeColor("FrameSystemButton.FgColor", pScheme);
		_disCol = GetSchemeColor("FrameSystemButton.BgColor", pScheme);
		
		const char *pEnabledImage = m_EnabledImage.Length() ? m_EnabledImage.Get() : 
			pScheme->GetResourceString( "FrameSystemButton.Icon" );
		const char *pDisabledImage = m_DisabledImage.Length() ? m_DisabledImage.Get() : 
			pScheme->GetResourceString( "FrameSystemButton.DisabledIcon" );
		_enabled = scheme()->GetImage( pEnabledImage, false);
		_disabled = scheme()->GetImage( pDisabledImage, false);

		SetTextInset(0, 0);
	
		// get our iconic image
		SetEnabled(IsEnabled());
	}
	
	virtual IBorder *GetBorder(bool depressed, bool armed, bool selected, bool keyfocus)
	{
		return NULL;
	}

	virtual void SetEnabled(bool state)
	{
		Button::SetEnabled(state);
		
		if (IsEnabled())
		{
			if ( _enabled )
			{
				SetImageAtIndex(0, _enabled, 0);
			}
			SetBgColor(_enCol);
			SetDefaultColor(_enCol, _enCol);
			SetArmedColor(_enCol, _enCol);
			SetDepressedColor(_enCol, _enCol);
		}
		else
		{
			if ( _disabled )
			{
				SetImageAtIndex(0, _disabled, 0);
			}
			SetBgColor(_disCol);
			SetDefaultColor(_disCol, _disCol);
			SetArmedColor(_disCol, _disCol);
			SetDepressedColor(_disCol, _disCol);
		}
	}
	
	void SetResponsive(bool state)
	{
		_respond = state;
	}

	virtual void OnMousePressed(MouseCode code)
	{
		// button may look enabled but not be responsive
		if (!_respond)
			return;

		BaseClass::OnMousePressed(code);
	}

	virtual void OnMouseDoublePressed(MouseCode code)
	{
		// button may look enabled but not be responsive
		if (!_respond)
			return;

		// only close if left is double pressed 
		if (code == MOUSE_LEFT)
		{
			// double click on the icon closes the window
			// But only if the menu contains a 'close' item
			vgui::Menu *pMenu = GetMenu();
			if ( pMenu && pMenu->FindChildByName("Close") )
			{
				PostMessage(GetVParent(), new KeyValues("CloseFrameButtonPressed"));
			}
		}
	}

};

} // namespace vgui
//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
Frame::Frame(Panel *parent, const char *panelName, bool showTaskbarIcon /*=true*/, bool bPopup /*=true*/ ) : EditablePanel(parent, panelName)
{
	// frames start invisible, to avoid having window flicker in on taskbar
	SetVisible(false);
	if ( bPopup )
	{
		MakePopup(showTaskbarIcon);
	}

	m_hPreviousModal = 0;

	_title=null;
	_moveable=true;
	_sizeable=true;
	m_bHasFocus=false;
	_flashWindow=false;
	_drawTitleBar = true; 
	m_bPreviouslyVisible = false;
	m_bFadingOut = false;
	m_bDisableFadeEffect = false;
	m_flTransitionEffectTime = 0.0f;
	m_flFocusTransitionEffectTime = 0.0f;
	m_bDeleteSelfOnClose = false;
	m_iClientInsetX = 5; 
	m_iClientInsetY = 5;
	m_iClientInsetXOverridden = false;
	m_iTitleTextInsetX = 28;
	m_bClipToParent = false;
	m_bSmallCaption = false;
	m_bChainKeysToParent = false;
	m_bPrimed = false;
	m_hCustomTitleFont = INVALID_FONT;

	SetTitle("#Frame_Untitled", parent ? false : true);
	
	// add ourselves to the build group
	SetBuildGroup(GetBuildGroup());
	
	SetMinimumSize(128,66);
	
	GetFocusNavGroup().SetFocusTopLevel(true);
	
#if !defined( _X360 )
	_sysMenu = NULL;

	// add dragging grips
	_topGrip = new GripPanel(this, "frame_topGrip", 0, -1);
	_bottomGrip = new GripPanel(this, "frame_bottomGrip", 0, 1);
	_leftGrip = new GripPanel(this, "frame_leftGrip", -1, 0);
	_rightGrip = new GripPanel(this, "frame_rightGrip", 1, 0);
	_topLeftGrip = new GripPanel(this, "frame_tlGrip", -1, -1);
	_topRightGrip = new GripPanel(this, "frame_trGrip", 1, -1);
	_bottomLeftGrip = new GripPanel(this, "frame_blGrip", -1, 1);
	_bottomRightGrip = new GripPanel(this, "frame_brGrip", 1, 1);
	_captionGrip = new CaptionGripPanel(this, "frame_caption" );
	_captionGrip->SetCursor(dc_arrow);

	_minimizeButton = new FrameButton(this, "frame_minimize","0");
	_minimizeButton->AddActionSignalTarget(this);
	_minimizeButton->SetCommand(new KeyValues("Minimize"));
	
	_maximizeButton = new FrameButton(this, "frame_maximize", "1");
	//!! no maximize handler implemented yet, so leave maximize button disabled
	SetMaximizeButtonVisible(false);

	char str[] = { 0x6F, 0 };
	_minimizeToSysTrayButton = new FrameButton(this, "frame_mintosystray", str);
	_minimizeToSysTrayButton->SetCommand("MinimizeToSysTray");
	SetMinimizeToSysTrayButtonVisible(false);
	
	_closeButton = new FrameButton(this, "frame_close", "r");
	_closeButton->AddActionSignalTarget(this);
	_closeButton->SetCommand(new KeyValues("CloseFrameButtonPressed"));
	
	if (!surface()->SupportsFeature(ISurface::FRAME_MINIMIZE_MAXIMIZE))
	{
		SetMinimizeButtonVisible(false);
		SetMaximizeButtonVisible(false);
	}

	if (parent)
	{
		// vgui doesn't support subwindow minimization
		SetMinimizeButtonVisible(false);
		SetMaximizeButtonVisible(false);
	}

	_menuButton = new FrameSystemButton(this, "frame_menu");
	_menuButton->SetMenu(GetSysMenu());
#endif
	
	SetupResizeCursors();

	REGISTER_COLOR_AS_OVERRIDABLE( m_InFocusBgColor, "infocus_bgcolor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( m_OutOfFocusBgColor, "outoffocus_bgcolor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _titleBarBgColor, "titlebarbgcolor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _titleBarDisabledBgColor, "titlebardisabledbgcolor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _titleBarFgColor, "titlebarfgcolor_override" );
	REGISTER_COLOR_AS_OVERRIDABLE( _titleBarDisabledFgColor, "titlebardisabledfgcolor_override" );
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
Frame::~Frame()
{
	if ( input()->GetAppModalSurface() == GetVPanel() )
	{
		vgui::input()->ReleaseAppModalSurface();
		if ( m_hPreviousModal != 0 )
		{
			vgui::input()->SetAppModalSurface( m_hPreviousModal );
			m_hPreviousModal = 0;
		}
	}

#if !defined( _X360 )
	delete _topGrip;
	delete _bottomGrip;
	delete _leftGrip;
	delete _rightGrip;
	delete _topLeftGrip;
	delete _topRightGrip;
	delete _bottomLeftGrip;
	delete _bottomRightGrip;
	delete _captionGrip;
	delete _minimizeButton;
	delete _maximizeButton;
	delete _closeButton;
	delete _menuButton;
	delete _minimizeToSysTrayButton;
#endif
	delete _title;
}

//-----------------------------------------------------------------------------
// Purpose: Setup the grips on the edges of the panel to resize it.
//-----------------------------------------------------------------------------
void Frame::SetupResizeCursors()
{
#if !defined( _X360 )
	if (IsSizeable())
	{
		_topGrip->SetCursor(dc_sizens);
		_bottomGrip->SetCursor(dc_sizens);
		_leftGrip->SetCursor(dc_sizewe);
		_rightGrip->SetCursor(dc_sizewe);
		_topLeftGrip->SetCursor(dc_sizenwse);
		_topRightGrip->SetCursor(dc_sizenesw);
		_bottomLeftGrip->SetCursor(dc_sizenesw);
		_bottomRightGrip->SetCursor(dc_sizenwse);

		_bottomRightGrip->SetPaintEnabled(true);
		_bottomRightGrip->SetPaintBackgroundEnabled(true);
	}
	else
	{
		// not resizable, so just use the default cursor
		_topGrip->SetCursor(dc_arrow);
		_bottomGrip->SetCursor(dc_arrow);
		_leftGrip->SetCursor(dc_arrow);
		_rightGrip->SetCursor(dc_arrow);
		_topLeftGrip->SetCursor(dc_arrow);
		_topRightGrip->SetCursor(dc_arrow);
		_bottomLeftGrip->SetCursor(dc_arrow);
		_bottomRightGrip->SetCursor(dc_arrow);

		_bottomRightGrip->SetPaintEnabled(false);
		_bottomRightGrip->SetPaintBackgroundEnabled(false);
	}
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Bring the frame to the front and requests focus, ensures it's not minimized
//-----------------------------------------------------------------------------
void Frame::Activate()
{
	MoveToFront();
	if ( IsKeyBoardInputEnabled() )
	{
		RequestFocus();
	}
	SetVisible(true);
	SetEnabled(true);
	if (m_bFadingOut)
	{
		// we were fading out, make sure to fade back in
		m_bFadingOut = false;
		m_bPreviouslyVisible = false;
	}

	surface()->SetMinimized(GetVPanel(), false);
}


//-----------------------------------------------------------------------------
// Sets up, cleans up modal dialogs
//-----------------------------------------------------------------------------
void Frame::DoModal( )
{
	// move to the middle of the screen
	MoveToCenterOfScreen();
	InvalidateLayout();
	Activate();
	m_hPreviousModal = vgui::input()->GetAppModalSurface();
	vgui::input()->SetAppModalSurface( GetVPanel() );
}


//-----------------------------------------------------------------------------
// Closes a modal dialog
//-----------------------------------------------------------------------------
void Frame::CloseModal()
{
	vgui::input()->ReleaseAppModalSurface();
	if ( m_hPreviousModal != 0 )
	{
		vgui::input()->SetAppModalSurface( m_hPreviousModal );
		m_hPreviousModal = 0;
	}
	PostMessage( this, new KeyValues("Close") );
}


//-----------------------------------------------------------------------------
// Purpose: activates the dialog 
//			if dialog is not currently visible it starts it minimized and flashing in the taskbar
//-----------------------------------------------------------------------------
void Frame::ActivateMinimized()
{
	if ( ( IsVisible() && !IsMinimized() ) || !surface()->SupportsFeature( ISurface::FRAME_MINIMIZE_MAXIMIZE ) )
	{
		Activate();
	}
	else
	{
		ipanel()->MoveToBack(GetVPanel());
		surface()->SetMinimized(GetVPanel(), true);
		SetVisible(true);
		SetEnabled(true);
		if (m_bFadingOut)
		{
			// we were fading out, make sure to fade back in
			m_bFadingOut = false;
			m_bPreviouslyVisible = false;
		}
		FlashWindow();
	}
}

//-----------------------------------------------------------------------------
// Purpose: returns true if the dialog is currently minimized
//-----------------------------------------------------------------------------
bool Frame::IsMinimized()
{
	return surface()->IsMinimized(GetVPanel());
}

//-----------------------------------------------------------------------------
// Purpose: Center the dialog on the screen
//-----------------------------------------------------------------------------
void Frame::MoveToCenterOfScreen()
{
	int wx, wy, ww, wt;
	surface()->GetWorkspaceBounds(wx, wy, ww, wt);
	SetPos((ww - GetWide()) / 2, (wt - GetTall()) / 2);
}


void Frame::LayoutProportional( FrameButton *bt )
{
	float scale = 1.0;

	if( IsProportional() )
	{	
		int screenW, screenH;
		surface()->GetScreenSize( screenW, screenH );

		int proW,proH;
		surface()->GetProportionalBase( proW, proH );

		scale =	( (float)( screenH ) / (float)( proH ) );
	}

	bt->SetSize( (int)( FrameButton::GetButtonSide( this ) * scale ), (int)( FrameButton::GetButtonSide( this ) * scale ) );
	bt->SetTextInset( (int)( ceil( 2 * scale ) ), (int) ( ceil(1 * scale ) ) );
}

//-----------------------------------------------------------------------------
// Purpose: per-frame thinking, used for transition effects
//			only gets called if the Frame is visible
//-----------------------------------------------------------------------------
void Frame::OnThink()
{
	BaseClass::OnThink();

	// check for transition effects
	if (IsVisible() && m_flTransitionEffectTime > 0 && ( !m_bDisableFadeEffect ))
	{
		if (m_bFadingOut)
		{
			// we're fading out, see if we're done so we can fully hide the window
			if (GetAlpha() < ( IsX360() ? 64 : 1 ))
			{
				FinishClose();
			}
		}
		else if (!m_bPreviouslyVisible)
		{
			// need to fade-in
			m_bPreviouslyVisible = true;
			
			// fade in
			if (IsX360())
			{
				SetAlpha(64);
			}
			else
			{
				SetAlpha(0);
			}
			GetAnimationController()->RunAnimationCommand(this, "alpha", 255.0f, 0.0f, m_flTransitionEffectTime, AnimationController::INTERPOLATOR_LINEAR);
		}
	}

	// check for focus changes
	bool hasFocus = false;

    if (input())
    {
	    VPANEL focus = input()->GetFocus();
	    if (focus && ipanel()->HasParent(focus, GetVPanel()))
	    {
		    if ( input()->GetAppModalSurface() == 0 || 
			    input()->GetAppModalSurface() == GetVPanel() )
		    {
			    hasFocus = true;
		    }
	    }
    }
	if (hasFocus != m_bHasFocus)
	{
		// Because vgui focus is message based, and focus gets reset to NULL when a focused panel is deleted, we defer the flashing/transition
		//  animation for an extra frame in case something is deleted, a message is sent, and then we become the focused panel again on the
		//  next frame
		if ( !m_bPrimed )
		{
			m_bPrimed = true;
			return;
		}
		m_bPrimed = false;
		m_bHasFocus = hasFocus;
		OnFrameFocusChanged(m_bHasFocus);
	}
	else
	{
		m_bPrimed = false;
	}
}

//-----------------------------------------------------------------------------
// Purpose: Called when the frame focus changes
//-----------------------------------------------------------------------------
void Frame::OnFrameFocusChanged(bool bHasFocus)
{
#if !defined( _X360 )
	// enable/disable the frame buttons
	_minimizeButton->SetDisabledLook(!bHasFocus);
	_maximizeButton->SetDisabledLook(!bHasFocus);
	_closeButton->SetDisabledLook(!bHasFocus);
	_minimizeToSysTrayButton->SetDisabledLook(!bHasFocus);
	_menuButton->SetEnabled(bHasFocus);
	_minimizeButton->InvalidateLayout();
	_maximizeButton->InvalidateLayout();
	_minimizeToSysTrayButton->InvalidateLayout();
	_closeButton->InvalidateLayout();
	_menuButton->InvalidateLayout();
#endif

	if (bHasFocus)
	{
		_title->SetColor(_titleBarFgColor);
	}
	else
	{
		_title->SetColor(_titleBarDisabledFgColor);
	}

	// set our background color
	if (bHasFocus)
	{
		if (m_flFocusTransitionEffectTime && ( !m_bDisableFadeEffect ))
		{
			GetAnimationController()->RunAnimationCommand(this, "BgColor", m_InFocusBgColor, 0.0f, m_bDisableFadeEffect ? 0.0f : m_flTransitionEffectTime, AnimationController::INTERPOLATOR_LINEAR);
		}
		else
		{
			SetBgColor(m_InFocusBgColor);
		}
	}
	else
	{
		if (m_flFocusTransitionEffectTime && ( !m_bDisableFadeEffect ))
		{
			GetAnimationController()->RunAnimationCommand(this, "BgColor", m_OutOfFocusBgColor, 0.0f, m_bDisableFadeEffect ? 0.0f : m_flTransitionEffectTime, AnimationController::INTERPOLATOR_LINEAR);
		}
		else
		{
			SetBgColor(m_OutOfFocusBgColor);
		}
	}

	// Stop flashing when we get focus
	if (bHasFocus && _flashWindow)
	{
		FlashWindowStop();
	}
}

int Frame::GetDraggerSize()
{
	const int DRAGGER_SIZE = 5;
	if ( m_bSmallCaption )
	{
		return 3;
	}
	
	return DRAGGER_SIZE;
}

int Frame::GetCornerSize()
{
	const int CORNER_SIZE = 8;
	if ( m_bSmallCaption )
	{
		return 6;
	}
	
	return CORNER_SIZE;
}

int Frame::GetBottomRightSize()
{
	const int BOTTOMRIGHTSIZE = 18;
	if ( m_bSmallCaption )
	{
		return 12;
	}
	
	return BOTTOMRIGHTSIZE;
}

int Frame::GetCaptionHeight()
{
	const int CAPTIONHEIGHT = 23;
	if ( m_bSmallCaption )
	{
		return 12;
	}
	return CAPTIONHEIGHT;
}

//-----------------------------------------------------------------------------
// Purpose: Recalculate the position of all items
//-----------------------------------------------------------------------------
void Frame::PerformLayout()
{
	// chain back
	BaseClass::PerformLayout();
	
	// move everything into place
	int wide, tall;
	GetSize(wide, tall);
		
#if !defined( _X360 )
	int DRAGGER_SIZE = GetDraggerSize();
	int CORNER_SIZE = GetCornerSize();
	int CORNER_SIZE2 = CORNER_SIZE * 2;
	int BOTTOMRIGHTSIZE = GetBottomRightSize();

	_topGrip->SetBounds(CORNER_SIZE, 0, wide - CORNER_SIZE2, DRAGGER_SIZE);
	_leftGrip->SetBounds(0, CORNER_SIZE, DRAGGER_SIZE, tall - CORNER_SIZE2);
	_topLeftGrip->SetBounds(0, 0, CORNER_SIZE, CORNER_SIZE);
	_topRightGrip->SetBounds(wide - CORNER_SIZE, 0, CORNER_SIZE, CORNER_SIZE);
	_bottomLeftGrip->SetBounds(0, tall - CORNER_SIZE, CORNER_SIZE, CORNER_SIZE);

	// make the bottom-right grip larger
	_bottomGrip->SetBounds(CORNER_SIZE, tall - DRAGGER_SIZE, wide - (CORNER_SIZE + BOTTOMRIGHTSIZE), DRAGGER_SIZE);
	_rightGrip->SetBounds(wide - DRAGGER_SIZE, CORNER_SIZE, DRAGGER_SIZE, tall - (CORNER_SIZE + BOTTOMRIGHTSIZE));

	_bottomRightGrip->SetBounds(wide - BOTTOMRIGHTSIZE, tall - BOTTOMRIGHTSIZE, BOTTOMRIGHTSIZE, BOTTOMRIGHTSIZE);
	
	_captionGrip->SetSize(wide-10,GetCaptionHeight());
	
	_topGrip->MoveToFront();
	_bottomGrip->MoveToFront();
	_leftGrip->MoveToFront();
	_rightGrip->MoveToFront();
	_topLeftGrip->MoveToFront();
	_topRightGrip->MoveToFront();
	_bottomLeftGrip->MoveToFront();
	_bottomRightGrip->MoveToFront();
	
	_maximizeButton->MoveToFront();
	_menuButton->MoveToFront();
	_minimizeButton->MoveToFront();
	_minimizeToSysTrayButton->MoveToFront();
	_menuButton->SetBounds(5+2, 5+3, GetCaptionHeight()-5, GetCaptionHeight()-5);
#endif

	float scale = 1;
	if (IsProportional())
	{
		int screenW, screenH;
		surface()->GetScreenSize( screenW, screenH );

		int proW,proH;
		surface()->GetProportionalBase( proW, proH );

		scale =	( (float)( screenH ) / (float)( proH ) );
	}
	
#if !defined( _X360 )
	int offset_start = (int)( 20 * scale );
	int offset = offset_start;

	int top_border_offset = (int) ( ( 5+3 ) * scale );
	if ( m_bSmallCaption )
	{
		top_border_offset = (int) ( ( 3 ) * scale );
	}

	int side_border_offset = (int) ( 5 * scale );
	// push the buttons against the east side
	if (_closeButton->IsVisible())
	{
		_closeButton->SetPos((wide-side_border_offset)-offset,top_border_offset);
		offset += offset_start;
		LayoutProportional( _closeButton );

	}
	if (_minimizeToSysTrayButton->IsVisible())
	{
		_minimizeToSysTrayButton->SetPos((wide-side_border_offset)-offset,top_border_offset);
		offset += offset_start;
		LayoutProportional( _minimizeToSysTrayButton );
	}
	if (_maximizeButton->IsVisible())
	{
		_maximizeButton->SetPos((wide-side_border_offset)-offset,top_border_offset);
		offset += offset_start;
		LayoutProportional( _maximizeButton );
	}
	if (_minimizeButton->IsVisible())
	{
		_minimizeButton->SetPos((wide-side_border_offset)-offset,top_border_offset);
		offset += offset_start;
		LayoutProportional( _minimizeButton );
	}
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Set the text in the title bar.
//-----------------------------------------------------------------------------
void Frame::SetTitle(const char *title, bool surfaceTitle)
{
	if (!_title)
	{
		_title = new TextImage( "" );
	}

	Assert(title);
	_title->SetText(title);

    // see if the combobox text has changed, and if so, post a message detailing the new text
	const char *newTitle = title;

	// check if the new text is a localized string, if so undo it
	wchar_t unicodeText[128];
	unicodeText[0] = 0;
	if (*newTitle == '#')
	{
		// try lookup in localization tables
		StringIndex_t unlocalizedTextSymbol = g_pVGuiLocalize->FindIndex(newTitle + 1);
		if (unlocalizedTextSymbol != INVALID_LOCALIZE_STRING_INDEX)
		{
			// we have a new text value
			wcsncpy( unicodeText, g_pVGuiLocalize->GetValueByIndex(unlocalizedTextSymbol), sizeof( unicodeText) / sizeof(wchar_t) );
		}
	}
	else
	{
		g_pVGuiLocalize->ConvertANSIToUnicode( newTitle, unicodeText, sizeof(unicodeText) );
	}

	if (surfaceTitle)
	{
		surface()->SetTitle(GetVPanel(), unicodeText);
	}
	
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: Sets the unicode text in the title bar
//-----------------------------------------------------------------------------
void Frame::SetTitle(const wchar_t *title, bool surfaceTitle)
{
	if (!_title)
	{
		_title = new TextImage( "" );
	}
	_title->SetText(title);
	if (surfaceTitle)
	{
		surface()->SetTitle(GetVPanel(), title);
	}
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: Set the text in the title bar.
//-----------------------------------------------------------------------------
void Frame::InternalSetTitle(const char *title)
{
	SetTitle(title, true);
}

//-----------------------------------------------------------------------------
// Purpose: Set the movability of the panel
//-----------------------------------------------------------------------------
void Frame::SetMoveable(bool state)
{
	_moveable=state;
}

//-----------------------------------------------------------------------------
// Purpose: Set the resizability of the panel
//-----------------------------------------------------------------------------
void Frame::SetSizeable(bool state)
{
	_sizeable=state;
	
	SetupResizeCursors();
}

// When moving via caption, don't let any part of window go outside parent's bounds
void Frame::SetClipToParent( bool state )
{
	m_bClipToParent = state;
}

bool Frame::GetClipToParent() const
{
	return m_bClipToParent;
}

//-----------------------------------------------------------------------------
// Purpose: Check the movability of the panel
//-----------------------------------------------------------------------------
bool Frame::IsMoveable()
{
	return _moveable;
}

//-----------------------------------------------------------------------------
// Purpose: Check the resizability of the panel
//-----------------------------------------------------------------------------
bool Frame::IsSizeable()
{
	return _sizeable;
}

//-----------------------------------------------------------------------------
// Purpose: Get the size of the panel inside the frame edges.
//-----------------------------------------------------------------------------
void Frame::GetClientArea(int &x, int &y, int &wide, int &tall)
{
	x = m_iClientInsetX;

	GetSize(wide, tall);

	if (_drawTitleBar)
	{
		int captionTall = surface()->GetFontTall(_title->GetFont());

		int border = m_bSmallCaption ? CAPTION_TITLE_BORDER_SMALL : CAPTION_TITLE_BORDER;
		int yinset = m_bSmallCaption ? 0 : m_iClientInsetY;

		yinset += m_iTitleTextInsetYOverride;

		y = yinset + captionTall + border + 1;
		tall = (tall - yinset) - y;
	}
	
	if ( m_bSmallCaption )
	{
		tall -= 5;
	}

	wide = (wide - m_iClientInsetX) - x;
}

// 
//-----------------------------------------------------------------------------
// Purpose: applies user configuration settings
//-----------------------------------------------------------------------------
void Frame::ApplyUserConfigSettings(KeyValues *userConfig)
{
	// calculate defaults
	int wx, wy, ww, wt;
	vgui::surface()->GetWorkspaceBounds(wx, wy, ww, wt);

	int x, y, wide, tall;
	GetBounds(x, y, wide, tall);
	bool bNoSettings = false;
	if (_moveable)
	{
		// check to see if anything is set
		if (!userConfig->FindKey("xpos", false))
		{
			bNoSettings = true;
		}

		// get the user config position
		// default to where we're currently at
		x = userConfig->GetInt("xpos", x);
		y = userConfig->GetInt("ypos", y);
	}
	if (_sizeable)
	{
		wide = userConfig->GetInt("wide", wide);
		tall = userConfig->GetInt("tall", tall);

		// Make sure it's no larger than the workspace
		if ( wide > ww )
		{
			wide = ww;
		}
		if ( tall > wt )
		{
			tall = wt; 
		}
	}

	// see if the dialog has a place on the screen it wants to start
	if (bNoSettings && GetDefaultScreenPosition(x, y, wide, tall))
	{
		bNoSettings = false;
	}

	// make sure it conforms to the minimum size of the dialog
	int minWide, minTall;
	GetMinimumSize(minWide, minTall);
	if (wide < minWide)
	{
		wide = minWide;
	}
	if (tall < minTall)
	{
		tall = minTall;
	}

	// make sure it's on the screen
	if (x + wide > ww)
	{
		x = wx + ww - wide;
	}
	if (y + tall > wt)
	{
		y = wy + wt - tall;
	}

	if (x < wx)
	{
		x = wx;
	}
	if (y < wy)
	{
		y = wy;
	}

	SetBounds(x, y, wide, tall);

	if (bNoSettings)
	{
		// since nothing was set, default our position to the middle of the screen
		MoveToCenterOfScreen();
	}

	BaseClass::ApplyUserConfigSettings(userConfig);
}

//-----------------------------------------------------------------------------
// Purpose: returns user config settings for this control
//-----------------------------------------------------------------------------
void Frame::GetUserConfigSettings(KeyValues *userConfig)
{
	if (_moveable)
	{
		int x, y;
		GetPos(x, y);
		userConfig->SetInt("xpos", x);
		userConfig->SetInt("ypos", y);
	}
	if (_sizeable)
	{
		int w, t;
		GetSize(w, t);
		userConfig->SetInt("wide", w);
		userConfig->SetInt("tall", t);
	}

	BaseClass::GetUserConfigSettings(userConfig);
}

//-----------------------------------------------------------------------------
// Purpose: optimization, return true if this control has any user config settings
//-----------------------------------------------------------------------------
bool Frame::HasUserConfigSettings()
{
	return true;
}

//-----------------------------------------------------------------------------
// Purpose: gets the default position and size on the screen to appear the first time (defaults to centered)
//-----------------------------------------------------------------------------
bool Frame::GetDefaultScreenPosition(int &x, int &y, int &wide, int &tall)
{
	return false;
}

//-----------------------------------------------------------------------------
// Purpose: draws title bar
//-----------------------------------------------------------------------------
void Frame::PaintBackground()
{
	// take the panel with focus and check up tree for this panel
	// if you find it, than some child of you has the focus, so
	// you should be focused
	Color titleColor = _titleBarDisabledBgColor;
	if (m_bHasFocus)
	{
		titleColor = _titleBarBgColor;
	}

	BaseClass::PaintBackground();

	if (_drawTitleBar)
	{
		int wide = GetWide();
		int tall = surface()->GetFontTall(_title->GetFont());

		// caption
		surface()->DrawSetColor(titleColor);
		int inset = m_bSmallCaption ? 3 : 5;
		int captionHeight = m_bSmallCaption ? 14: 28;

		surface()->DrawFilledRect(inset, inset, wide - inset, captionHeight );
		
		if (_title)
		{
			int nTitleX = m_iTitleTextInsetXOverride ? m_iTitleTextInsetXOverride : m_iTitleTextInsetX;
			int nTitleWidth = wide - 72;
#if !defined( _X360 )
			if ( _menuButton && _menuButton->IsVisible() )
			{
				int mw, mh;
				_menuButton->GetImageSize( mw, mh );
				nTitleX += mw;
				nTitleWidth -= mw;
			}
#endif
			int nTitleY;
			if ( m_iTitleTextInsetYOverride )
			{
				nTitleY = m_iTitleTextInsetYOverride;
			}
			else
			{
				nTitleY = m_bSmallCaption ? 2 : 9;
			}
			_title->SetPos( nTitleX, nTitleY );		
			_title->SetSize( nTitleWidth, tall);
			_title->Paint();
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Frame::ApplySchemeSettings(IScheme *pScheme)
{
	// always chain back
	BaseClass::ApplySchemeSettings(pScheme);
	
	SetOverridableColor( &_titleBarFgColor, GetSchemeColor("FrameTitleBar.TextColor", pScheme) );
	SetOverridableColor( &_titleBarBgColor, GetSchemeColor("FrameTitleBar.BgColor", pScheme) );
	SetOverridableColor( &_titleBarDisabledFgColor, GetSchemeColor("FrameTitleBar.DisabledTextColor", pScheme) );
	SetOverridableColor( &_titleBarDisabledBgColor, GetSchemeColor("FrameTitleBar.DisabledBgColor", pScheme) );

	const char *font = NULL;
	if ( m_bSmallCaption )
	{
		font = pScheme->GetResourceString("FrameTitleBar.SmallFont");
	}
	else
	{
		font = pScheme->GetResourceString("FrameTitleBar.Font");
	}

	HFont titlefont;
	if ( m_hCustomTitleFont )
	{
		titlefont = m_hCustomTitleFont;
	}
	else
	{
		titlefont = pScheme->GetFont((font && *font) ? font : "Default", IsProportional());
	}

	_title->SetFont( titlefont );
	_title->ResizeImageToContent();

#if !defined( _X360 )
	HFont marfont = (HFont)0;
	if ( m_bSmallCaption )
	{
		marfont = pScheme->GetFont( "MarlettSmall", IsProportional() );
	}
	else
	{
		marfont = pScheme->GetFont( "Marlett", IsProportional() );
	}

	_minimizeButton->SetFont(marfont);
	_maximizeButton->SetFont(marfont);
	_minimizeToSysTrayButton->SetFont(marfont);
	_closeButton->SetFont(marfont);
#endif

	m_flTransitionEffectTime = atof(pScheme->GetResourceString("Frame.TransitionEffectTime"));
	m_flFocusTransitionEffectTime = atof(pScheme->GetResourceString("Frame.FocusTransitionEffectTime"));

	SetOverridableColor( &m_InFocusBgColor, pScheme->GetColor("Frame.BgColor", GetBgColor()) );
	SetOverridableColor( &m_OutOfFocusBgColor, pScheme->GetColor("Frame.OutOfFocusBgColor", m_InFocusBgColor) );

	const char *resourceString = pScheme->GetResourceString("Frame.ClientInsetX");
	if ( resourceString )
	{
		m_iClientInsetX = atoi(resourceString);
	}
	resourceString = pScheme->GetResourceString("Frame.ClientInsetY");
	if ( resourceString )
	{
		m_iClientInsetY = atoi(resourceString);
	}
	resourceString = pScheme->GetResourceString("Frame.TitleTextInsetX");
	if ( resourceString )
	{
		m_iTitleTextInsetX = atoi(resourceString);
	}

	SetBgColor(m_InFocusBgColor);
	SetBorder(pScheme->GetBorder("FrameBorder"));

	OnFrameFocusChanged( m_bHasFocus );
}

// Disables the fade-in/out-effect even if configured in the scheme settings
void Frame::DisableFadeEffect( void )
{
	m_flFocusTransitionEffectTime = 0.f;
	m_flTransitionEffectTime = 0.f;
}

void Frame::SetFadeEffectDisableOverride( bool disabled )
{
	m_bDisableFadeEffect = disabled;
}

//-----------------------------------------------------------------------------
// Purpose: Apply settings loaded from a resource file
//-----------------------------------------------------------------------------
void Frame::ApplySettings(KeyValues *inResourceData)
{
	// Don't change the frame's visibility, remove that setting from the config data
	inResourceData->SetInt("visible", -1);
	BaseClass::ApplySettings(inResourceData);

	SetCloseButtonVisible( inResourceData->GetBool( "setclosebuttonvisible", true ) );

	if( !inResourceData->GetInt("settitlebarvisible", 1 ) ) // if "title" is "0" then don't draw the title bar
	{
		SetTitleBarVisible( false );
	}
	
	// set the title
	const char *title = inResourceData->GetString("title", "");
	if (title && *title)
	{
		SetTitle(title, true);
	}

	const char *titlefont = inResourceData->GetString("title_font", "");
	if ( titlefont && titlefont[0] )
	{
		IScheme *pScheme = scheme()->GetIScheme( GetScheme() );
		if ( pScheme )
		{
			m_hCustomTitleFont = pScheme->GetFont( titlefont );
		}
	}

	KeyValues *pKV = inResourceData->FindKey( "clientinsetx_override", false );
	if ( pKV )
	{
		m_iClientInsetX = pKV->GetInt();
		m_iClientInsetXOverridden = true;
	}
}

//-----------------------------------------------------------------------------
// Purpose: Apply settings loaded from a resource file
//-----------------------------------------------------------------------------
void Frame::GetSettings(KeyValues *outResourceData)
{
	BaseClass::GetSettings(outResourceData);
	outResourceData->SetInt("settitlebarvisible", _drawTitleBar );

	if (_title)
	{
		char buf[256];
		_title->GetUnlocalizedText( buf, 255 );
		if (buf[0])
		{
			outResourceData->SetString("title", buf);
		}
	}

	if ( m_iClientInsetXOverridden )
	{
		outResourceData->SetInt( "clientinsetx_override", m_iClientInsetX );
	}
}

//-----------------------------------------------------------------------------
// Purpose: returns a description of the settings possible for a frame
//-----------------------------------------------------------------------------
const char *Frame::GetDescription()
{
	static char buf[512];
	Q_snprintf(buf, sizeof(buf), "%s, string title", BaseClass::GetDescription());
	return buf;
}

//-----------------------------------------------------------------------------
// Purpose: Go invisible when a close message is recieved.
//-----------------------------------------------------------------------------
void Frame::OnClose()
{
	// if we're modal, release that before we hide the window else the wrong window will get focus
	if (input()->GetAppModalSurface() == GetVPanel())
	{
		input()->ReleaseAppModalSurface();
		if ( m_hPreviousModal != 0 )
		{
			vgui::input()->SetAppModalSurface( m_hPreviousModal );
			m_hPreviousModal = 0;
		}
	}
	
	BaseClass::OnClose();

	if (m_flTransitionEffectTime && !m_bDisableFadeEffect)
	{
		// begin the hide transition effect
		GetAnimationController()->RunAnimationCommand(this, "alpha", 0.0f, 0.0f, m_flTransitionEffectTime, AnimationController::INTERPOLATOR_LINEAR);
		m_bFadingOut = true;
		// move us to the back of the draw order (so that fading out over the top of other dialogs doesn't look wierd)
		surface()->MovePopupToBack(GetVPanel());
	}
	else
	{
		// hide us immediately
		FinishClose();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Close button in frame pressed
//-----------------------------------------------------------------------------
void Frame::OnCloseFrameButtonPressed()
{
	OnCommand("Close");
}

//-----------------------------------------------------------------------------
// Purpose: Command handling
//-----------------------------------------------------------------------------
void Frame::OnCommand(const char *command)
{
	if (!stricmp(command, "Close"))
	{
		Close();
	}
	else if (!stricmp(command, "CloseModal"))
	{
		CloseModal();
	}
	else if (!stricmp(command, "Minimize"))
	{
		OnMinimize();
	}
	else if (!stricmp(command, "MinimizeToSysTray"))
	{
		OnMinimizeToSysTray();
	}
	else
	{
		BaseClass::OnCommand(command);
	}
}


//-----------------------------------------------------------------------------
// Purpose: Get the system menu 
//-----------------------------------------------------------------------------
Menu *Frame::GetSysMenu()
{
#if !defined( _X360 )
	if (!_sysMenu)
	{
		_sysMenu = new Menu(this, NULL);
		_sysMenu->SetVisible(false);
		_sysMenu->AddActionSignalTarget(this);

		_sysMenu->AddMenuItem("Minimize", "#SysMenu_Minimize", "Minimize", this);
		_sysMenu->AddMenuItem("Maximize", "#SysMenu_Maximize", "Maximize", this);
		_sysMenu->AddMenuItem("Close", "#SysMenu_Close", "Close", this);

		// check for enabling/disabling menu items
		// this might have to be done at other times as well. 
		Panel *menuItem = _sysMenu->FindChildByName("Minimize");
		if (menuItem)
		{
			menuItem->SetEnabled(_minimizeButton->IsVisible());
		}
		menuItem = _sysMenu->FindChildByName("Maximize");
		if (menuItem)
		{
			menuItem->SetEnabled(_maximizeButton->IsVisible());
		}
		menuItem = _sysMenu->FindChildByName("Close");
		if (menuItem)
		{
			menuItem->SetEnabled(_closeButton->IsVisible());
		}
	}
	
	return _sysMenu;
#else
	return NULL;
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Set the system menu  
//-----------------------------------------------------------------------------
void Frame::SetSysMenu(Menu *menu)
{
#if !defined( _X360 )
	if (menu == _sysMenu)
		return;
	
	_sysMenu->MarkForDeletion();
	_sysMenu = menu;

	_menuButton->SetMenu(_sysMenu);
#endif
}


//-----------------------------------------------------------------------------
// Set the system menu images
//-----------------------------------------------------------------------------
void Frame::SetImages( const char *pEnabledImage, const char *pDisabledImage )
{
#if !defined( _X360 )
	_menuButton->SetImages( pEnabledImage, pDisabledImage );
#endif
}


//-----------------------------------------------------------------------------
// Purpose: Close the window 
//-----------------------------------------------------------------------------
void Frame::Close()
{
	OnClose();
}

//-----------------------------------------------------------------------------
// Purpose: Finishes closing the dialog
//-----------------------------------------------------------------------------
void Frame::FinishClose()
{
	SetVisible(false);
	m_bPreviouslyVisible = false;
	m_bFadingOut = false;

	OnFinishedClose();
	
	if (m_bDeleteSelfOnClose)
	{
		// Must be last because if vgui is not running then this will call delete this!!!
		MarkForDeletion();
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Frame::OnFinishedClose()
{
}

//-----------------------------------------------------------------------------
// Purpose: Minimize the window on the taskbar.
//-----------------------------------------------------------------------------
void Frame::OnMinimize()
{
	surface()->SetMinimized(GetVPanel(), true);
}

//-----------------------------------------------------------------------------
// Purpose: Does nothing by default
//-----------------------------------------------------------------------------
void Frame::OnMinimizeToSysTray()
{
}

//-----------------------------------------------------------------------------
// Purpose: Respond to mouse presses
//-----------------------------------------------------------------------------
void Frame::OnMousePressed(MouseCode code)
{
	if (!IsBuildGroupEnabled())
	{
		// if a child doesn't have focus, get it for ourselves
		VPANEL focus = input()->GetFocus();
		if (!focus || !ipanel()->HasParent(focus, GetVPanel()))
		{
			RequestFocus();
		}
	}
	
	BaseClass::OnMousePressed(code);
}

//-----------------------------------------------------------------------------
// Purpose: Toggle visibility of the system menu button
//-----------------------------------------------------------------------------
void Frame::SetMenuButtonVisible(bool state)
{
#if !defined( _X360 )
	_menuButton->SetVisible(state);
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Toggle respond of the system menu button
//			it will look enabled or disabled in response to the title bar
//			but may not activate.
//-----------------------------------------------------------------------------
void Frame::SetMenuButtonResponsive(bool state)
{
#if !defined( _X360 )
	_menuButton->SetResponsive(state);
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Toggle visibility of the minimize button
//-----------------------------------------------------------------------------
void Frame::SetMinimizeButtonVisible(bool state)
{
#if !defined( _X360 )
	_minimizeButton->SetVisible(state);
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Toggle visibility of the maximize button
//-----------------------------------------------------------------------------
void Frame::SetMaximizeButtonVisible(bool state)
{
#if !defined( _X360 )
	_maximizeButton->SetVisible(state);
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Toggles visibility of the minimize-to-systray icon (defaults to false)
//-----------------------------------------------------------------------------
void Frame::SetMinimizeToSysTrayButtonVisible(bool state)
{
#if !defined( _X360 )
	_minimizeToSysTrayButton->SetVisible(state);
#endif
}

//-----------------------------------------------------------------------------
// Purpose: Toggle visibility of the close button
//-----------------------------------------------------------------------------
void Frame::SetCloseButtonVisible(bool state)
{
#if !defined( _X360 )
	_closeButton->SetVisible(state);
#endif
}

//-----------------------------------------------------------------------------
// Purpose: soaks up any remaining messages
//-----------------------------------------------------------------------------
void Frame::OnKeyCodeReleased(KeyCode code)
{
}

//-----------------------------------------------------------------------------
// Purpose: soaks up any remaining messages
//-----------------------------------------------------------------------------
void Frame::OnKeyFocusTicked()
{
}

//-----------------------------------------------------------------------------
// Purpose: Toggles window flash state on a timer
//-----------------------------------------------------------------------------
void Frame::InternalFlashWindow()
{
	if (_flashWindow)
	{
		// toggle icon flashing
		_nextFlashState = true;
		surface()->FlashWindow(GetVPanel(), _nextFlashState);
		_nextFlashState = !_nextFlashState;
		
		PostMessage(this, new KeyValues("FlashWindow"), 1.8f);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Adds the child to the focus nav group
//-----------------------------------------------------------------------------
void Frame::OnChildAdded(VPANEL child)
{
	BaseClass::OnChildAdded(child);
}

//-----------------------------------------------------------------------------
// Purpose: Flash the window system tray button until the frame gets focus
//-----------------------------------------------------------------------------
void Frame::FlashWindow()
{
	_flashWindow = true;
	_nextFlashState = true;
	
	InternalFlashWindow();
}

//-----------------------------------------------------------------------------
// Purpose: Stops any window flashing
//-----------------------------------------------------------------------------
void Frame::FlashWindowStop()
{
	surface()->FlashWindow(GetVPanel(), false);
	_flashWindow = false;
}


//-----------------------------------------------------------------------------
// Purpose: load the control settings - should be done after all the children are added to the dialog
//-----------------------------------------------------------------------------
void Frame::LoadControlSettings( const char *dialogResourceName, const char *pathID, KeyValues *pPreloadedKeyValues, KeyValues *pConditions )
{
	BaseClass::LoadControlSettings( dialogResourceName, pathID, pPreloadedKeyValues, pConditions );

	// set the focus on the default control
	Panel *defaultFocus = GetFocusNavGroup().GetDefaultPanel();
	if (defaultFocus)
	{
		defaultFocus->RequestFocus();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Checks for ctrl+shift+b hits to enter build mode
//			Activates any hotkeys / default buttons
//			Swallows any unhandled input
//-----------------------------------------------------------------------------
void Frame::OnKeyCodeTyped(KeyCode code)
{
	bool shift = (input()->IsKeyDown(KEY_LSHIFT) || input()->IsKeyDown(KEY_RSHIFT));
	bool ctrl = (input()->IsKeyDown(KEY_LCONTROL) || input()->IsKeyDown(KEY_RCONTROL));
	bool alt = (input()->IsKeyDown(KEY_LALT) || input()->IsKeyDown(KEY_RALT));
	
	if ( IsX360() )
	{
		vgui::Panel *pMap = FindChildByName( "ControllerMap" );
		if ( pMap && pMap->IsKeyBoardInputEnabled() )
		{
			pMap->OnKeyCodeTyped( code );
			return;
		}
	}

	if ( ctrl && shift && alt && code == KEY_B)
	{
		// enable build mode
		ActivateBuildMode();
	}
	else if (ctrl && shift && alt && code == KEY_R)
	{
		// reload the scheme
		VPANEL top = surface()->GetEmbeddedPanel();
		if (top)
		{
			// reload the data file
			scheme()->ReloadSchemes();

			Panel *panel = ipanel()->GetPanel(top, GetModuleName());
			if (panel)
			{
				// make the top-level panel reload it's scheme, it will chain down to all the child panels
				panel->InvalidateLayout(false, true);
			}
		}
	}
	else if (alt && code == KEY_F4)
	{
		// user has hit the close
		PostMessage(this, new KeyValues("CloseFrameButtonPressed"));
	}
	else if (code == KEY_ENTER)
	{
		// check for a default button
		VPANEL panel = GetFocusNavGroup().GetCurrentDefaultButton();
		if (panel && ipanel()->IsVisible( panel ) && ipanel()->IsEnabled( panel ))
		{
			// Activate the button
			PostMessage(panel, new KeyValues("Hotkey"));
		}
	}
	else if ( code == KEY_ESCAPE && 
		surface()->SupportsFeature(ISurface::ESCAPE_KEY) && 
		input()->GetAppModalSurface() == GetVPanel() )
	{
		// ESC cancels, unless we're in the engine - in the engine ESC flips between the UI and the game
		CloseModal();
	}
	// Usually don't chain back as Frames are the end of the line for key presses, unless
	// m_bChainKeysToParent is set
	else if ( m_bChainKeysToParent )
	{
		BaseClass::OnKeyCodeTyped( code );
	}
	else
	{
		input()->OnKeyCodeUnhandled( (int)code );
	}
}

//-----------------------------------------------------------------------------
// Purpose: If true, then OnKeyCodeTyped messages continue up past the Frame
// Input  : state - 
//-----------------------------------------------------------------------------
void Frame::SetChainKeysToParent( bool state )
{
	m_bChainKeysToParent = state;
}

//-----------------------------------------------------------------------------
// Purpose: If true, then OnKeyCodeTyped messages continue up past the Frame
// Input  :  - 
// Output : Returns true on success, false on failure.
//-----------------------------------------------------------------------------
bool Frame::CanChainKeysToParent() const
{
	return m_bChainKeysToParent;
}

//-----------------------------------------------------------------------------
// Purpose: Checks for ctrl+shift+b hits to enter build mode
//			Activates any hotkeys / default buttons
//			Swallows any unhandled input
//-----------------------------------------------------------------------------
void Frame::OnKeyTyped(wchar_t unichar)
{
	Panel *panel = GetFocusNavGroup().FindPanelByHotkey(unichar);
	if (panel)
	{
		// tell the panel to Activate
		PostMessage(panel, new KeyValues("Hotkey"));
	}
}

//-----------------------------------------------------------------------------
// Purpose: sets all title bar controls
//-----------------------------------------------------------------------------
void Frame::SetTitleBarVisible( bool state )
{
	_drawTitleBar = state; 
	SetMenuButtonVisible(state);
	SetMinimizeButtonVisible(state);
	SetMaximizeButtonVisible(state);
	SetCloseButtonVisible(state);
}

//-----------------------------------------------------------------------------
// Purpose: sets the frame to delete itself on close
//-----------------------------------------------------------------------------
void Frame::SetDeleteSelfOnClose( bool state )
{
	m_bDeleteSelfOnClose = state;
}

//-----------------------------------------------------------------------------
// Purpose: updates localized text
//-----------------------------------------------------------------------------
void Frame::OnDialogVariablesChanged( KeyValues *dialogVariables )
{
	StringIndex_t index = _title->GetUnlocalizedTextSymbol();
	if (index != INVALID_LOCALIZE_STRING_INDEX)
	{
		// reconstruct the string from the variables
		wchar_t buf[1024];
		g_pVGuiLocalize->ConstructString(buf, sizeof(buf), index, dialogVariables);
		SetTitle(buf, true);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Handles staying on screen when the screen size changes
//-----------------------------------------------------------------------------
void Frame::OnScreenSizeChanged(int iOldWide, int iOldTall)
{
	BaseClass::OnScreenSizeChanged(iOldWide, iOldTall);

	if (IsProportional())
		return;

	// make sure we're completely on screen
	int iNewWide, iNewTall;
	surface()->GetScreenSize(iNewWide, iNewTall);

	int x, y, wide, tall;
	GetBounds(x, y, wide, tall);

	// make sure the bottom-right corner is on the screen first
	if (x + wide > iNewWide)
	{
		x = iNewWide - wide;
	}
	if (y + tall > iNewTall)
	{
		y = iNewTall - tall;
	}

	// make sure the top-left is visible
	x = max( 0, x );
	y = max( 0, y );

	// apply
	SetPos(x, y);
}

//-----------------------------------------------------------------------------
// Purpose: For supporting thin caption bars
// Input  : state - 
//-----------------------------------------------------------------------------
void Frame::SetSmallCaption( bool state )
{
	m_bSmallCaption = state;
	InvalidateLayout();
}

//-----------------------------------------------------------------------------
// Purpose: 
// Input  :  - 
// Output : Returns true on success, false on failure.
//-----------------------------------------------------------------------------
bool Frame::IsSmallCaption() const
{
	return m_bSmallCaption;
}


//-----------------------------------------------------------------------------
// Purpose: Static method to place a frame under the cursor
//-----------------------------------------------------------------------------
void Frame::PlaceUnderCursor( )
{
	// get cursor position, this is local to this text edit window
	int cursorX, cursorY;
	input()->GetCursorPos( cursorX, cursorY );

	// relayout the menu immediately so that we know it's size
	InvalidateLayout(true);
	int w, h;
	GetSize( w, h );

	// work out where the cursor is and therefore the best place to put the frame
	int sw, sh;
	surface()->GetScreenSize( sw, sh );

	// Try to center it first
	int x, y;
	x = cursorX - ( w / 2 );
	y = cursorY - ( h / 2 );

	// Clamp to various sides
	if ( x + w > sw )
	{
		x = sw - w;
	}
	if ( y + h > sh )
	{
		y = sh - h;
	}
	if ( x < 0 )
	{
		x = 0;
	}
	if ( y < 0 )
	{
		y = 0;
	}

	SetPos( x, y );
}

//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: 
//
// $NoKeywords: $
//=============================================================================//

#define PROTECTED_THINGS_DISABLE

#include "vgui/Cursor.h"
#include "vgui/IInput.h"
#include "vgui/ILocalize.h"
#include "vgui/IScheme.h"
#include "vgui/ISurface.h"
#include "vgui/IPanel.h"
#include "KeyValues.h"

#include "vgui_controls/ComboBox.h"
#include "vgui_controls/Menu.h"
#include "vgui_controls/MenuItem.h"
#include "vgui_controls/TextImage.h"

#include <ctype.h>

// memdbgon must be the last include file in a .cpp file!!!
#include "tier0/memdbgon.h"

using namespace vgui;

namespace vgui
{
ComboBoxButton::ComboBoxButton(ComboBox *parent, const char *panelName, const char *text) : Button(parent, panelName, text)
{
	SetButtonActivationType(ACTIVATE_ONPRESSED);
}

void ComboBoxButton::ApplySchemeSettings(IScheme *pScheme)
{
	Button::ApplySchemeSettings(pScheme);
	
	SetFont(pScheme->GetFont("Marlett", IsProportional()));
	SetContentAlignment(Label::a_west);
#ifdef OSX
	SetTextInset(-3, 0);
#else
	SetTextInset(3, 0);
#endif
	SetDefaultBorder(pScheme->GetBorder("ScrollBarButtonBorder"));
	
	// arrow changes color but the background doesnt.
	SetDefaultColor(GetSchemeColor("ComboBoxButton.ArrowColor", pScheme), GetSchemeColor("ComboBoxButton.BgColor", pScheme));
	SetArmedColor(GetSchemeColor("ComboBoxButton.ArmedArrowColor", pScheme), GetSchemeColor("ComboBoxButton.BgColor", pScheme));
	SetDepressedColor(GetSchemeColor("ComboBoxButton.ArmedArrowColor", pScheme), GetSchemeColor("ComboBoxButton.BgColor", pScheme));
	m_DisabledBgColor = GetSchemeColor("ComboBoxButton.DisabledBgColor", pScheme);
}

IBorder * ComboBoxButton::GetBorder(bool depressed, bool armed, bool selected, bool keyfocus)
{
	return NULL;
	//		return Button::GetBorder(depressed, armed, selected, keyfocus);
}

//-----------------------------------------------------------------------------
// Purpose: Dim the arrow on the button when exiting the box
//			only if the menu is closed, so let the parent handle this.
//-----------------------------------------------------------------------------
void ComboBoxButton::OnCursorExited()
{
	// want the arrow to go grey when we exit the box if the menu is not open
	CallParentFunction(new KeyValues("CursorExited"));
}

} // namespace vgui

vgui::Panel *ComboBox_Factory()
{
	return new ComboBox( NULL, NULL, 5, true );
}
DECLARE_BUILD_FACTORY_CUSTOM( ComboBox, ComboBox_Factory );

//-----------------------------------------------------------------------------
// Purpose: Constructor
// Input  : parent - parent class
//			panelName
//			numLines - number of lines in dropdown menu
//			allowEdit - whether combobox is editable or not
//-----------------------------------------------------------------------------
ComboBox::ComboBox(Panel *parent, const char *panelName, int numLines, bool allowEdit ) : TextEntry(parent, panelName)
{
	SetEditable(allowEdit);
	SetHorizontalScrolling(false); // do not scroll, always Start at the beginning of the text.

	// create the drop-down menu
	m_pDropDown = new Menu(this, NULL);
	m_pDropDown->AddActionSignalTarget(this);
	m_pDropDown->SetTypeAheadMode( Menu::TYPE_AHEAD_MODE );

	// button to Activate menu
	m_pButton = new ComboBoxButton(this, "Button", "u");
	m_pButton->SetCommand("ButtonClicked");
	m_pButton->AddActionSignalTarget(this);

	SetNumberOfEditLines(numLines);

	m_bHighlight = false;
	m_iDirection = Menu::DOWN;
	m_iOpenOffsetY = 0;
	m_bPreventTextChangeMessage = false;
	m_szBorderOverride[0] = '\0';
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
ComboBox::~ComboBox()
{
	m_pDropDown->DeletePanel();
	m_pButton->DeletePanel();
}

//-----------------------------------------------------------------------------
// Purpose: Set the number of items in the dropdown menu.
// Input  : numLines -  number of items in dropdown menu
//-----------------------------------------------------------------------------
void ComboBox::SetNumberOfEditLines( int numLines )
{
	m_pDropDown->SetNumberOfVisibleItems( numLines );
}

//-----------------------------------------------------------------------------
// Purpose: Add an item to the drop down
// Input  : char *itemText - name of dropdown menu item
//-----------------------------------------------------------------------------
int ComboBox::AddItem(const char *itemText, const KeyValues *userData)
{
	// when the menu item is selected it will send the custom message "SetText"
	return m_pDropDown->AddMenuItem( itemText, new KeyValues("SetText", "text", itemText), this, userData );
}


//-----------------------------------------------------------------------------
// Purpose: Add an item to the drop down
// Input  : char *itemText - name of dropdown menu item
//-----------------------------------------------------------------------------
int ComboBox::AddItem(const wchar_t *itemText, const KeyValues *userData)
{
	// add the element to the menu
	// when the menu item is selected it will send the custom message "SetText"
	KeyValues *kv = new KeyValues("SetText");
	kv->SetWString("text", itemText);
	// get an ansi version for the menuitem name
	char ansi[128];
	g_pVGuiLocalize->ConvertUnicodeToANSI(itemText, ansi, sizeof(ansi));
	return m_pDropDown->AddMenuItem(ansi, kv, this, userData);
}


//-----------------------------------------------------------------------------
// Removes a single item
//-----------------------------------------------------------------------------
void ComboBox::DeleteItem( int itemID )
{
	if ( !m_pDropDown->IsValidMenuID(itemID))
		return;

	m_pDropDown->DeleteItem( itemID );
}


//-----------------------------------------------------------------------------
// Purpose: Updates a current item to the drop down
// Input  : char *itemText - name of dropdown menu item
//-----------------------------------------------------------------------------
bool ComboBox::UpdateItem(int itemID, const char *itemText, const KeyValues *userData)
{
	if ( !m_pDropDown->IsValidMenuID(itemID))
		return false;

	// when the menu item is selected it will send the custom message "SetText"
	m_pDropDown->UpdateMenuItem(itemID, itemText, new KeyValues("SetText", "text", itemText), userData);
	InvalidateLayout();
	return true;
}
//-----------------------------------------------------------------------------
// Purpose: Updates a current item to the drop down
// Input  : wchar_t *itemText - name of dropdown menu item
//-----------------------------------------------------------------------------
bool ComboBox::UpdateItem(int itemID, const wchar_t *itemText, const KeyValues *userData)
{
	if ( !m_pDropDown->IsValidMenuID(itemID))
		return false;

	// when the menu item is selected it will send the custom message "SetText"
	KeyValues *kv = new KeyValues("SetText");
	kv->SetWString("text", itemText);
	m_pDropDown->UpdateMenuItem(itemID, itemText, kv, userData);
	InvalidateLayout();
	return true;
}

//-----------------------------------------------------------------------------
// Purpose: Updates a current item to the drop down
// Input  : wchar_t *itemText - name of dropdown menu item
//-----------------------------------------------------------------------------
bool ComboBox::IsItemIDValid( int itemID )
{
	return m_pDropDown->IsValidMenuID(itemID);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ComboBox::SetItemEnabled(const char *itemText, bool state)
{
	m_pDropDown->SetItemEnabled(itemText, state);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ComboBox::SetItemEnabled(int itemID, bool state)
{
	m_pDropDown->SetItemEnabled(itemID, state);
}

//-----------------------------------------------------------------------------
// Purpose: Remove all items from the drop down menu
//-----------------------------------------------------------------------------
void ComboBox::RemoveAll()
{
	m_pDropDown->DeleteAllItems();
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
int ComboBox::GetItemCount()
{
	return m_pDropDown->GetItemCount();
}

int ComboBox::GetItemIDFromRow( int row )
{
	// valid from [0, GetItemCount)
	return m_pDropDown->GetMenuID( row );
}

//-----------------------------------------------------------------------------
// Purpose: Activate the item in the menu list, as if that menu item had been selected by the user
// Input  : itemID - itemID from AddItem in list of dropdown items
//-----------------------------------------------------------------------------
void ComboBox::ActivateItem(int itemID)
{
	m_pDropDown->ActivateItem(itemID);
}

//-----------------------------------------------------------------------------
// Purpose: Activate the item in the menu list, as if that menu item had been selected by the user
// Input  : itemID - itemID from AddItem in list of dropdown items
//-----------------------------------------------------------------------------
void ComboBox::ActivateItemByRow(int row)
{
	m_pDropDown->ActivateItemByRow(row);
}

//-----------------------------------------------------------------------------
// Purpose: Activate the item in the menu list, without sending a TextChanged message
// Input  : row - row to activate
//-----------------------------------------------------------------------------
void ComboBox::SilentActivateItemByRow(int row)
{
	int itemID = GetItemIDFromRow( row );
	if ( itemID >= 0 )
	{
		SilentActivateItem( itemID );
	}
}

//-----------------------------------------------------------------------------
// Purpose: Activate the item in the menu list, without sending a TextChanged message
// Input  : itemID - itemID from AddItem in list of dropdown items
//-----------------------------------------------------------------------------
void ComboBox::SilentActivateItem(int itemID)
{
	m_pDropDown->SilentActivateItem(itemID);

	// Now manually call our set text, with a wrapper to ensure we don't send the Text Changed message
	wchar_t name[ 256 ];
	GetItemText( itemID, name, sizeof( name ) );

	m_bPreventTextChangeMessage = true;
	OnSetText( name );
	m_bPreventTextChangeMessage = false;
}

//-----------------------------------------------------------------------------
// Purpose: Allows a custom menu to be used with the combo box
//-----------------------------------------------------------------------------
void ComboBox::SetMenu( Menu *menu )
{
	if ( m_pDropDown )
	{
		m_pDropDown->MarkForDeletion();
	}

	m_pDropDown = menu;
	if ( m_pDropDown )
	{
		m_pDropDown->SetParent( this );
	}
}

//-----------------------------------------------------------------------------
// Purpose: Layout the format of the combo box for drawing on screen
//-----------------------------------------------------------------------------
void ComboBox::PerformLayout()
{
	int wide, tall;
	GetPaintSize(wide, tall);

	BaseClass::PerformLayout();

	HFont buttonFont = m_pButton->GetFont();
	int fontTall = surface()->GetFontTall( buttonFont );

	int buttonSize = min( tall, fontTall );
	
	int buttonY = ( ( tall - 1 ) - buttonSize ) / 2;

	// Some dropdown button icons in our games are wider than they are taller. We need to factor that in.
	int button_wide, button_tall;
	m_pButton->GetContentSize(button_wide, button_tall);
	button_wide = max( buttonSize, button_wide );

	m_pButton->SetBounds( wide - button_wide, buttonY, button_wide, buttonSize );
	if ( IsEditable() )
	{
		SetCursor(dc_ibeam);
	}
	else
	{
		SetCursor(dc_arrow);
	}

	m_pButton->SetEnabled(IsEnabled());

	DoMenuLayout();
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ComboBox::DoMenuLayout()
{
	m_pDropDown->PositionRelativeToPanel( this, m_iDirection, m_iOpenOffsetY );

	// reset the width of the drop down menu to be the width of the combo box
	m_pDropDown->SetFixedWidth(GetWide());
	m_pDropDown->ForceCalculateWidth();

}

//-----------------------------------------------------------------------------
// Purpose: Sorts the items in the list
//-----------------------------------------------------------------------------
void ComboBox::SortItems( void )
{
}

//-----------------------------------------------------------------------------
// Purpose: return the index of the last selected item
//-----------------------------------------------------------------------------
int ComboBox::GetActiveItem()
{
	return m_pDropDown->GetActiveItem();
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
KeyValues *ComboBox::GetActiveItemUserData()
{
	return m_pDropDown->GetItemUserData(GetActiveItem());
}	


//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
KeyValues *ComboBox::GetItemUserData(int itemID)
{
	return m_pDropDown->GetItemUserData(itemID);
}	


//-----------------------------------------------------------------------------
// Purpose: data accessor
//-----------------------------------------------------------------------------
void ComboBox::GetItemText( int itemID, wchar_t *text, int bufLenInBytes )
{
	m_pDropDown->GetItemText( itemID, text, bufLenInBytes );
}

void ComboBox::GetItemText( int itemID, char *text, int bufLenInBytes )
{
	m_pDropDown->GetItemText( itemID, text, bufLenInBytes );
}


//-----------------------------------------------------------------------------
// Purpose: 
// Output : Returns true on success, false on failure.
//-----------------------------------------------------------------------------
bool ComboBox::IsDropdownVisible()
{
	return m_pDropDown->IsVisible();
}

//-----------------------------------------------------------------------------
// Purpose: 
// Input  : *inResourceData - 
//-----------------------------------------------------------------------------
void ComboBox::ApplySchemeSettings(IScheme *pScheme)
{
	BaseClass::ApplySchemeSettings(pScheme);

	SetBorder( pScheme->GetBorder( m_szBorderOverride[0] ? m_szBorderOverride : "ComboBoxBorder" ) );
}

void ComboBox::ApplySettings( KeyValues *pInResourceData )
{
	BaseClass::ApplySettings( pInResourceData );

	const char *pBorderOverride = pInResourceData->GetString( "border_override", NULL );
	if ( pBorderOverride )
	{
		V_strncpy( m_szBorderOverride, pBorderOverride, sizeof( m_szBorderOverride ) );
	}

	KeyValues *pKVButton = pInResourceData->FindKey( "Button" );
	if ( pKVButton && m_pButton )
	{
		m_pButton->ApplySettings( pKVButton );
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set the visiblity of the drop down menu button.
//-----------------------------------------------------------------------------
void ComboBox::SetDropdownButtonVisible(bool state)
{
	m_pButton->SetVisible(state);
}

//-----------------------------------------------------------------------------
// Purpose: overloads TextEntry MousePressed
//-----------------------------------------------------------------------------
void ComboBox::OnMousePressed(MouseCode code)
{
	if ( !m_pDropDown )
		return;

	if ( !IsEnabled() )
		return;

	// make sure it's getting pressed over us (it may not be due to mouse capture)
	if ( !IsCursorOver() )
	{
		HideMenu();
		return;
	}

	if ( IsEditable() )
	{
		BaseClass::OnMousePressed(code);
		HideMenu();
	}
	else
	{
		// clicking on a non-editable text box just activates the drop down menu
		RequestFocus();
		DoClick();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Double-click acts the same as a single-click
//-----------------------------------------------------------------------------
void ComboBox::OnMouseDoublePressed(MouseCode code)
{
    if (IsEditable())
    {
        BaseClass::OnMouseDoublePressed(code);
    }
    else
    {
	    OnMousePressed(code);
    }
}

//-----------------------------------------------------------------------------
// Purpose: Called when a command is received from the menu
//			Changes the label text to be that of the command
// Input  : char *command - 
//-----------------------------------------------------------------------------
void ComboBox::OnCommand( const char *command )
{
	if (!stricmp(command, "ButtonClicked"))
	{
		// hide / show the menu underneath
		DoClick();
	}

	Panel::OnCommand(command);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ComboBox::OnSetText(const wchar_t *newtext)
{
	// see if the combobox text has changed, and if so, post a message detailing the new text
	const wchar_t *text = newtext;

	// check if the new text is a localized string, if so undo it
	if (*text == '#')
	{
		char cbuf[255];
		g_pVGuiLocalize->ConvertUnicodeToANSI(text, cbuf, 255);

		// try lookup in localization tables
		StringIndex_t unlocalizedTextSymbol = g_pVGuiLocalize->FindIndex(cbuf + 1);
		
		if (unlocalizedTextSymbol != INVALID_LOCALIZE_STRING_INDEX)
		{
			// we have a new text value
			text = g_pVGuiLocalize->GetValueByIndex(unlocalizedTextSymbol);
		}
	}

	wchar_t wbuf[255];
	GetText(wbuf, 254);
	
	if ( wcscmp(wbuf, text) )
	{
		// text has changed
		SetText(text);

		// fire off that things have changed
		if ( !m_bPreventTextChangeMessage )
		{
			PostActionSignal(new KeyValues("TextChanged", "text", text));
		}
		Repaint();
	}

	// close the box
	HideMenu();
}

//-----------------------------------------------------------------------------
// Purpose: hides the menu
//-----------------------------------------------------------------------------
void ComboBox::HideMenu(void)
{
	if ( !m_pDropDown )
		return;

	// hide the menu
	m_pDropDown->SetVisible(false);
	Repaint();
	OnHideMenu(m_pDropDown);
}

//-----------------------------------------------------------------------------
// Purpose: shows the menu
//-----------------------------------------------------------------------------
void ComboBox::ShowMenu(void)
{
	if ( !m_pDropDown )
		return;

	// hide the menu
	m_pDropDown->SetVisible(false);
	DoClick();
}

//-----------------------------------------------------------------------------
// Purpose: Called when the window loses focus; hides the menu
//-----------------------------------------------------------------------------
void ComboBox::OnKillFocus()
{
	SelectNoText();
}

//-----------------------------------------------------------------------------
// Purpose: Called when the menu is closed
//-----------------------------------------------------------------------------
void ComboBox::OnMenuClose()
{
	HideMenu();

	if ( HasFocus() )
	{
		SelectAllText(false);
	}
	else if ( m_bHighlight )
	{
		m_bHighlight = false;
        // we want the text to be highlighted when we request the focus
//		SelectAllOnFirstFocus(true);
        RequestFocus();
	}
	// if cursor is in this box or the arrow box
	else if ( IsCursorOver() )// make sure it's getting pressed over us (it may not be due to mouse capture)
	{
		SelectAllText(false);
		OnCursorEntered();
		// Get focus so the box will unhighlight if we click somewhere else.
		RequestFocus();
	}
	else
	{
		m_pButton->SetArmed(false);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Handles hotkey accesses
// FIXME: make this open different directions as necessary see menubutton.
//-----------------------------------------------------------------------------
void ComboBox::DoClick()
{
	// menu is already visible, hide the menu
	if ( m_pDropDown->IsVisible() )
	{
		HideMenu();
		return;
	}

	// do nothing if menu is not enabled
	if ( !m_pDropDown->IsEnabled() )
	{
		return;
	}
	// force the menu to Think
	m_pDropDown->PerformLayout();

	// make sure we're at the top of the draw order (and therefore our children as well)
	// RequestFocus();
	
	// We want the item that is shown in the combo box to show as selected
	int itemToSelect = -1;
	int i;
	wchar_t comboBoxContents[255];
	GetText(comboBoxContents, 255);
	for ( i = 0 ; i < m_pDropDown->GetItemCount() ; i++ )
	{
		wchar_t menuItemName[255];
		int menuID = m_pDropDown->GetMenuID(i);
		m_pDropDown->GetMenuItem(menuID)->GetText(menuItemName, 255);
		if (!wcscmp(menuItemName, comboBoxContents))
		{
			itemToSelect = i;
			break;
		}
	}
	// if we found a match, highlight it on opening the menu
	if ( itemToSelect >= 0 )
	{
		m_pDropDown->SetCurrentlyHighlightedItem( m_pDropDown->GetMenuID(itemToSelect) );
	}

	// reset the dropdown's position
	DoMenuLayout();


	// make sure we're at the top of the draw order (and therefore our children as well)
	// this important to make sure the menu will be drawn in the foreground
	MoveToFront();

	// !KLUDGE! Force alpha to solid.  Otherwise,
	// we run into weird VGUI problems with pops
	// and the stencil test
	Color c = m_pDropDown->GetBgColor();
	c[3] = 255;
	m_pDropDown->SetBgColor( c );

	// notify
	OnShowMenu(m_pDropDown);

	// show the menu
	m_pDropDown->SetVisible(true);

	// bring to focus
	m_pDropDown->RequestFocus();

	// no text is highlighted when the menu is opened
	SelectNoText();

	// highlight the arrow while menu is open
	m_pButton->SetArmed(true);

	Repaint();
}


//-----------------------------------------------------------------------------
// Purpose: Brighten the arrow on the button when entering the box
//-----------------------------------------------------------------------------
void ComboBox::OnCursorEntered()
{
	// want the arrow to go white when we enter the box 
	m_pButton->OnCursorEntered();
	TextEntry::OnCursorEntered();
}

//-----------------------------------------------------------------------------
// Purpose: Dim the arrow on the button when exiting the box
//-----------------------------------------------------------------------------
void ComboBox::OnCursorExited()
{
	// want the arrow to go grey when we exit the box if the menu is not open
	if ( !m_pDropDown->IsVisible() )
	{
		m_pButton->SetArmed(false);
		TextEntry::OnCursorExited();
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
#ifdef _X360
void ComboBox::OnMenuItemSelected()
{
	m_bHighlight = true;
	// For editable cbs, fill in the text field from whatever is chosen from the dropdown...

	//=============================================================================
	// HPE_BEGIN:
	// [pfreese] The text for the combo box should be updated regardless of its
	// editable state, and in any case, the member variable below was never 
	// correctly initialized.
	//=============================================================================
	
	// if ( m_bAllowEdit )
	
	//=============================================================================
	// HPE_END
	//=============================================================================
	{
		int idx = GetActiveItem();
		if ( idx >= 0 )
		{
			wchar_t name[ 256 ];
			GetItemText( idx, name, sizeof( name ) );

			OnSetText( name );
		}
	}

	Repaint();

	// go to the next control
	if(!NavigateDown())
	{
		NavigateUp();
	}
}
#else
void ComboBox::OnMenuItemSelected()
{
	m_bHighlight = true;
	// For editable cbs, fill in the text field from whatever is chosen from the dropdown...
	//if ( m_bAllowEdit )
	{
		int idx = GetActiveItem();
		if ( idx >= 0 )
		{
			wchar_t name[ 256 ];
			GetItemText( idx, name, sizeof( name ) );

			OnSetText( name );
		}
	}

	Repaint();
}
#endif

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ComboBox::OnSizeChanged(int wide, int tall)
{
	BaseClass::OnSizeChanged( wide, tall);

	// set the drawwidth.
	int bwide, btall;
	PerformLayout();
	m_pButton->GetSize( bwide, btall);
	SetDrawWidth( wide - bwide );
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
#ifdef _X360
void ComboBox::OnSetFocus()
{
    BaseClass::OnSetFocus();

	GotoTextEnd();
	SelectAllText(true);
}
#else
void ComboBox::OnSetFocus()
{
    BaseClass::OnSetFocus();

	GotoTextEnd();
	SelectAllText(false);
}
#endif

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
#ifdef _X360
void ComboBox::OnKeyCodePressed(KeyCode code)
{
	switch ( GetBaseButtonCode( code ) )
    {
	case KEY_XBUTTON_A:
		DoClick();
		break;
    case KEY_XBUTTON_UP:
	case KEY_XSTICK1_UP:
	case KEY_XSTICK2_UP:
		if(m_pDropDown->IsVisible())
		{
			MoveAlongMenuItemList(-1);
		}
		else
		{
			BaseClass::OnKeyCodePressed(code);
		}
        break;
    case KEY_XBUTTON_DOWN:
	case KEY_XSTICK1_DOWN:
	case KEY_XSTICK2_DOWN:
		if(m_pDropDown->IsVisible())
		{
			MoveAlongMenuItemList(1);
		}
		else
		{
			BaseClass::OnKeyCodePressed(code);
		}
        break;
    default:
        BaseClass::OnKeyCodePressed(code);
        break;
    }
}
#endif

//-----------------------------------------------------------------------------
// Purpose: Handles up/down arrows
//-----------------------------------------------------------------------------
void ComboBox::OnKeyCodeTyped(KeyCode code)
{
	bool alt = (input()->IsKeyDown(KEY_LALT) || input()->IsKeyDown(KEY_RALT));

	if (alt)
	{
		switch (code)
		{
		case KEY_UP:
		case KEY_DOWN:
			{
				DoClick();
				break;
			}
		default:
			{				
				BaseClass::OnKeyCodeTyped(code);
				break;
			}
		}
	}
	else
	{
		switch (code)
		{
		case KEY_HOME:
		case KEY_END:
		case KEY_PAGEUP:
		case KEY_PAGEDOWN:
		case KEY_UP:
		case KEY_DOWN:
			{
				int itemSelected = m_pDropDown->GetCurrentlyHighlightedItem();
				m_pDropDown->OnKeyCodeTyped(code);				
				int itemToSelect = m_pDropDown->GetCurrentlyHighlightedItem();

				if ( itemToSelect != itemSelected )
				{
					SelectMenuItem(itemToSelect);
				}
				break;
			}

		case KEY_ENTER:
			{
				int itemToSelect = m_pDropDown->GetCurrentlyHighlightedItem();
				m_pDropDown->ActivateItem(itemToSelect);
				break;
			}

		default:
			{
				BaseClass::OnKeyCodeTyped(code);
				break;
			}
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose: handles key input
//-----------------------------------------------------------------------------
void ComboBox::OnKeyTyped(wchar_t unichar)
{
	if ( IsEditable() || unichar == '\t') // don't play with key presses in edit mode
	{
		BaseClass::OnKeyTyped( unichar );
		return;
	}

	int itemSelected = m_pDropDown->GetCurrentlyHighlightedItem();
	m_pDropDown->OnKeyTyped(unichar);
	int itemToSelect = m_pDropDown->GetCurrentlyHighlightedItem();

	if ( itemToSelect != itemSelected )
    {
		SelectMenuItem(itemToSelect);
	}
	else
	{
		BaseClass::OnKeyTyped( unichar );
	}
}

void ComboBox::SelectMenuItem(int itemToSelect)
{
	// if we found this item, then we scroll up or down
	if ( itemToSelect >= 0 && itemToSelect < m_pDropDown->GetItemCount() )
	{
		wchar_t menuItemName[255];

		int menuID = m_pDropDown->GetMenuID(itemToSelect);
		m_pDropDown->GetMenuItem(menuID)->GetText(menuItemName, 254);
		OnSetText(menuItemName);
		SelectAllText(false);		
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ComboBox::MoveAlongMenuItemList(int direction)
{
	// We want the item that is shown in the combo box to show as selected
	int itemToSelect = -1;
    wchar_t menuItemName[255];
	int i;

	wchar_t comboBoxContents[255];
	GetText(comboBoxContents, 254);
	for ( i = 0 ; i < m_pDropDown->GetItemCount() ; i++ )
	{
		int menuID = m_pDropDown->GetMenuID(i);
		m_pDropDown->GetMenuItem(menuID)->GetText(menuItemName, 254);

		if ( !wcscmp(menuItemName, comboBoxContents) )
		{
			itemToSelect = i;
			break;
		}
	}

	if ( itemToSelect >= 0 )
	{
		int newItem = itemToSelect + direction;
		if ( newItem < 0 )
		{
			newItem = 0;
		}
		else if ( newItem >= m_pDropDown->GetItemCount() )
		{
			newItem = m_pDropDown->GetItemCount() - 1;
		}
		SelectMenuItem(newItem);
	}

}

void ComboBox::MoveToFirstMenuItem()
{
	SelectMenuItem(0);
}

void ComboBox::MoveToLastMenuItem()
{
	SelectMenuItem(m_pDropDown->GetItemCount() - 1);
}


//-----------------------------------------------------------------------------
// Purpose: Sets the direction from the menu button the menu should open
//-----------------------------------------------------------------------------
void ComboBox::SetOpenDirection(Menu::MenuDirection_e direction)
{
	m_iDirection = direction;
}

void ComboBox::SetFont( HFont font )
{
	BaseClass::SetFont( font );

	m_pDropDown->SetFont( font );
}


void ComboBox::SetUseFallbackFont( bool bState, HFont hFallback )
{
	BaseClass::SetUseFallbackFont( bState, hFallback );
	m_pDropDown->SetUseFallbackFont( bState, hFallback );
}

//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: 
//
// $NoKeywords: $
//=============================================================================//

#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <ctype.h>

#include <vgui/IInput.h>
#include <vgui/ILocalize.h>
#include <vgui/IPanel.h>
#include <vgui/ISurface.h>
#include <vgui/IScheme.h>
#include <KeyValues.h>

#include <vgui_controls/Label.h>
#include <vgui_controls/Image.h>
#include <vgui_controls/TextImage.h>
#include <vgui_controls/Controls.h>

// memdbgon must be the last include file in a .cpp file!!!
#include <tier0/memdbgon.h>

using namespace vgui;

#ifndef max
#define max(a,b)            (((a) > (b)) ? (a) : (b))
#endif

DECLARE_BUILD_FACTORY_DEFAULT_TEXT( Label, Label );

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
Label::Label(Panel *parent, const char *panelName, const char *text) : BaseClass(parent, panelName)
{
	Init();

	_textImage = new TextImage(text);
	_textImage->SetColor(Color(0, 0, 0, 0));
	SetText(text);
	_textImageIndex = AddImage(_textImage, 0);

	REGISTER_COLOR_AS_OVERRIDABLE( _disabledFgColor2, "disabledfgcolor2_override" );
}

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
Label::Label(Panel *parent, const char *panelName, const wchar_t *wszText) : BaseClass(parent, panelName)
{
	Init();

	_textImage = new TextImage(wszText);
	_textImage->SetColor(Color(0, 0, 0, 0));
	SetText(wszText);
	_textImageIndex = AddImage(_textImage, 0);

	REGISTER_COLOR_AS_OVERRIDABLE( _disabledFgColor2, "disabledfgcolor2_override" );
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
Label::~Label()
{
	delete _textImage;
	delete [] _associateName;
	delete [] _fontOverrideName;
}

//-----------------------------------------------------------------------------
// Purpose: Construct the label
//-----------------------------------------------------------------------------
void Label::Init()
{
	_contentAlignment = a_west;
	_textColorState = CS_NORMAL;
	_textInset[0] = 0;
	_textInset[1] = 0;
	_hotkey = 0;
	_associate = NULL;
	_associateName = NULL;
	_fontOverrideName = NULL;
	m_bWrap = false;
	m_bCenterWrap = false;
	m_bAutoWideToContents = false;
	m_bUseProportionalInsets = false;
	m_bAutoWideDirty = false;

//	SetPaintBackgroundEnabled(false);
}

//-----------------------------------------------------------------------------
// Purpose: Set whether the text is displayed bright or dull
//-----------------------------------------------------------------------------
void Label::SetTextColorState(EColorState state)
{
	if (_textColorState != state)
	{
		_textColorState = state;
		InvalidateLayout();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Return the full size of the contained content
//-----------------------------------------------------------------------------
void Label::GetContentSize(int &wide, int &tall)
{
	if( GetFont() == INVALID_FONT ) // we haven't loaded our font yet, so load it now
	{
		IScheme *pScheme = scheme()->GetIScheme( GetScheme() );
		if ( pScheme )
		{
			SetFont( pScheme->GetFont( "Default", IsProportional() ) );
		}
	}


	int tx0, ty0, tx1, ty1;
	ComputeAlignment(tx0, ty0, tx1, ty1);

	// the +8 is padding to the content size
	// the code which uses it should really set that itself; 
	// however a lot of existing code relies on this
	wide = (tx1 - tx0) + _textInset[0]; 

	// get the size of the text image and remove it
	int iWide, iTall;
	_textImage->GetSize(iWide, iTall);
	wide -=  iWide;
	// get the full, untruncated (no elipsis) size of the text image.
	_textImage->GetContentSize(iWide, iTall);
	wide += iWide;

	// addin the image offsets as well
	for (int i=0; i < _imageDar.Size(); i++)
		wide += _imageDar[i].offset;

	tall = max((ty1 - ty0) + _textInset[1], iTall);
}

//-----------------------------------------------------------------------------
// Purpose: Calculate the keyboard key that is a hotkey 
//-----------------------------------------------------------------------------
wchar_t Label::CalculateHotkey(const char *text)
{
	for (const char *ch = text; *ch != 0; ch++)
	{
		if (*ch == '&')
			{
			// get the next character
			ch++;

			if (*ch == '&')
			{
				// just an &
				continue;
			}
			else if (*ch == 0)
			{
				break;
			}
			else if (V_isalnum(*ch))
			{
				// found the hotkey
				return (wchar_t)tolower(*ch);
			}
		}
	}

	return '\0';
}

wchar_t Label::CalculateHotkey(const wchar_t *text)
{
	if( text )
	{
		for (const wchar_t *ch = text; *ch != 0; ch++)
		{
			if (*ch == '&')
			{
				// get the next character
				ch++;

				if (*ch == '&')
				{
					// just an &
					continue;
				}
				else if (*ch == 0)
				{
					break;
				}
				else if (iswalnum(*ch))
				{
					// found the hotkey
					return (wchar_t)towlower(*ch);
				}
			}
		}
	}

	return '\0';
}

//-----------------------------------------------------------------------------
// Purpose: Check if this label has a hotkey that is the key passed in.
//-----------------------------------------------------------------------------
Panel *Label::HasHotkey(wchar_t key)
{
#ifdef VGUI_HOTKEYS_ENABLED
	if ( iswalnum( key ) )
		key = towlower( key );

	if (_hotkey == key)
		return this;
#endif

	return NULL;
}

//-----------------------------------------------------------------------------
// Purpose: Set the hotkey for this label
//-----------------------------------------------------------------------------
void Label::SetHotkey(wchar_t ch)
{
	_hotkey = ch;
}

wchar_t Label::GetHotKey()
{
	return _hotkey;
}

//-----------------------------------------------------------------------------
// Purpose: Handle a hotkey by passing on focus to associate
//-----------------------------------------------------------------------------
void Label::OnHotkeyPressed()
{
	// we can't accept focus, but if we are associated to a control give it to that
	if (_associate.Get() && !IsBuildModeActive())
	{
		_associate->RequestFocus();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Redirect mouse pressed to giving focus to associate
//-----------------------------------------------------------------------------
void Label::OnMousePressed(MouseCode code)
{
	if (_associate.Get() && !IsBuildModeActive())
	{
		_associate->RequestFocus();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Return the text in the label
//-----------------------------------------------------------------------------
void Label::GetText(char *textOut, int bufferLen)
{
	_textImage->GetText(textOut, bufferLen);
}

//-----------------------------------------------------------------------------
// Purpose: Return the text in the label
//-----------------------------------------------------------------------------
void Label::GetText(wchar_t *textOut, int bufLenInBytes)
{
	_textImage->GetText(textOut, bufLenInBytes);
}

//-----------------------------------------------------------------------------
// Purpose: Take the string and looks it up in the localization file 
//          to convert it to unicode
//			Setting the text will not set the size of the label.
//			Set the size explicitly or use setToContent()
//-----------------------------------------------------------------------------
void Label::SetText(const char *text)
{
	// if set to null, just make blank
	if (!text)
	{
		text = "";
	}

	// let the text image do the translation itself
	_textImage->SetText(text);

	if( text[0] == '#' )
	{
		SetHotkey(CalculateHotkey(g_pVGuiLocalize->Find(text)));		
	}
	else
	{	
		SetHotkey(CalculateHotkey(text));
	}

	m_bAutoWideDirty = m_bAutoWideToContents;

	InvalidateLayout();
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: Set unicode text directly
//-----------------------------------------------------------------------------
void Label::SetText(const wchar_t *unicodeString, bool bClearUnlocalizedSymbol)
{
	m_bAutoWideDirty = m_bAutoWideToContents;

	if ( unicodeString && _textImage->GetUText() && !Q_wcscmp(unicodeString,_textImage->GetUText()) )
		return;

	_textImage->SetText(unicodeString, bClearUnlocalizedSymbol);

//!! need to calculate hotkey from translated string
	SetHotkey(CalculateHotkey(unicodeString));

    InvalidateLayout();     // possible that the textimage needs to expand
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: updates localized text
//-----------------------------------------------------------------------------
void Label::OnDialogVariablesChanged(KeyValues *dialogVariables )
{
	StringIndex_t index = _textImage->GetUnlocalizedTextSymbol();
	if (index != INVALID_LOCALIZE_STRING_INDEX)
	{
		// reconstruct the string from the variables
		wchar_t buf[1024];
		g_pVGuiLocalize->ConstructString(buf, sizeof(buf), index, dialogVariables);
		SetText(buf);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Additional offset at the Start of the text (from whichever side it is aligned)
//-----------------------------------------------------------------------------
void Label::SetTextInset(int xInset, int yInset)
{
	_textInset[0] = xInset;
	_textInset[1] = yInset;

	int wide, tall;
	GetSize( wide, tall);
	_textImage->SetDrawWidth(wide - _textInset[0]);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Label::GetTextInset(int *xInset, int *yInset )
{
	*xInset = _textInset[0];
	*yInset = _textInset[1];
}

//-----------------------------------------------------------------------------
// Purpose: Set the enabled state
//-----------------------------------------------------------------------------
void Label::SetEnabled(bool state)
{
	Panel::SetEnabled(state);
}

//-----------------------------------------------------------------------------
// Purpose: Calculates where in the panel the content resides
// Input  : &tx0 - [out] position of the content
//			&ty0 - 
//			&tx1 - 
//			&ty1 - 
// Note:	horizontal alignment is west if the image dar has
//			more than one image in it, this is because we use image sizes
//			to determine layout in classes for example, Menu.
//-----------------------------------------------------------------------------
void Label::ComputeAlignment(int &tx0, int &ty0, int &tx1, int &ty1)
{
	int wide, tall;
	GetPaintSize(wide, tall);
	int tWide,tTall;

	// text bounding box
	tx0 = 0;
	ty0 = 0;

	// loop through all the images and calculate the complete bounds
	int maxX = 0, maxY = 0;

	int actualXAlignment = _contentAlignment;
	for (int i = 0; i < _imageDar.Count(); i++)
	{
		TImageInfo &imageInfo = _imageDar[i];
		IImage *image = imageInfo.image;
		if (!image)
			continue; // skip over null images

		// add up the bounds
		int iWide, iTall;
		image->GetSize(iWide, iTall);
		if (iWide > wide) // if the image is larger than the label just do a west alignment
			actualXAlignment = Label::a_west;
		
		// get the max height
		maxY = max(maxY, iTall);
		maxX += iWide;

		// add the offset to x
		maxX += imageInfo.offset;
	}

	tWide = maxX;
	tTall = maxY;
	
	// x align text
	switch (actualXAlignment)
	{
		// left
		case Label::a_northwest:
		case Label::a_west:
		case Label::a_southwest:
		{
			tx0 = 0;
			break;
		}
		// center
		case Label::a_north:
		case Label::a_center:
		case Label::a_south:
		{
			tx0 = (wide - tWide) / 2;
			break;
		}
		// right
		case Label::a_northeast:
		case Label::a_east:
		case Label::a_southeast:
		{
			tx0 = wide - tWide;
			break;
		}
	}

	// y align text
	switch (_contentAlignment)
	{
		//top
		case Label::a_northwest:
		case Label::a_north:
		case Label::a_northeast:
		{
			ty0 = 0;
			break;
		}
		// center
		case Label::a_west:
		case Label::a_center:
		case Label::a_east:
		{
			ty0 = (tall - tTall) / 2;
			break;
		}
		// south
		case Label::a_southwest:
		case Label::a_south:
		case Label::a_southeast:
		{
			ty0 = tall - tTall;
			break;
		}
	}

	tx1 = tx0 + tWide;
	ty1 = ty0 + tTall;
}

//-----------------------------------------------------------------------------
// Purpose: overridden main drawing function for the panel
//-----------------------------------------------------------------------------
void Label::Paint()
{
	int tx0, ty0, tx1, ty1;
	ComputeAlignment(tx0, ty0, tx1, ty1);

	// calculate who our associate is if we haven't already
	if (_associateName)
	{
		SetAssociatedControl(FindSiblingByName(_associateName));
		delete [] _associateName;
		_associateName = NULL;
	}

	int labelWide, labelTall;
	GetSize(labelWide, labelTall);
	int x = tx0, y = _textInset[1] + ty0;
	int imageYPos = 0; // a place to save the y offset for when we draw the disable version of the image

	// draw the set of images
	for (int i = 0; i < _imageDar.Count(); i++)
	{
		TImageInfo &imageInfo = _imageDar[i];
		IImage *image = imageInfo.image;
		if (!image)
			continue; // skip over null images

		// add the offset to x
		x += imageInfo.offset;

		// if this is the text image then add its inset to the left or from the right
		if (i == _textImageIndex)
		{
			switch ( _contentAlignment )
			{
				// left
				case Label::a_northwest:
				case Label::a_west:
				case Label::a_southwest:
				{
					x += _textInset[0];
					break;
				}
				// right
				case Label::a_northeast:
				case Label::a_east:
				case Label::a_southeast:
				{
					x -= _textInset[0];
					break;
				}
			}
		}

		// see if the image is in a fixed position
		if (imageInfo.xpos >= 0)
		{
			x = imageInfo.xpos;
		}

		// draw
		imageYPos = y;
		image->SetPos(x, y);

		// fix up y for center-aligned text
		if (_contentAlignment == Label::a_west || _contentAlignment == Label::a_center || _contentAlignment == Label::a_east)
		{
			int iw, it;
			image->GetSize(iw, it);
			if (it < (ty1 - ty0))
			{
				imageYPos = ((ty1 - ty0) - it) / 2 + y;
				image->SetPos(x, ((ty1 - ty0) - it) / 2 + y);
			}
		}

		// don't resize the image unless its too big
		if (imageInfo.width >= 0)
		{
			int w, t;
			image->GetSize(w, t);
			if (w > imageInfo.width)
			{
				image->SetSize(imageInfo.width, t);
			}
		}

		// if it's the basic text image then draw specially
		if (image == _textImage)
		{
			if (IsEnabled())
			{
				if (_associate.Get() && ipanel()->HasParent(input()->GetFocus(), _associate->GetVPanel()))
				{
					_textImage->SetColor(_associateColor);
				}
				else
				{
					_textImage->SetColor(GetFgColor());
				}

				_textImage->Paint();
			}
			else
			{
				// draw disabled version, with embossed look
				// offset image
				_textImage->SetPos(x + 1, imageYPos + 1);
				_textImage->SetColor(_disabledFgColor1);
				_textImage->Paint();

				surface()->DrawFlushText();

				// overlayed image
				_textImage->SetPos(x, imageYPos);
				_textImage->SetColor(_disabledFgColor2);
				_textImage->Paint();
			}
		}
		else
		{
			image->Paint();
		}

		// add the image size to x
		int wide, tall;
		image->GetSize(wide, tall);
		x += wide;
	}
}


//-----------------------------------------------------------------------------
// Purpose: Helper function, draws a simple line with dashing parameters
//-----------------------------------------------------------------------------
void Label::DrawDashedLine(int x0, int y0, int x1, int y1, int dashLen, int gapLen)
{
	// work out which way the line goes
	if ((x1 - x0) > (y1 - y0))
	{
		// x direction line
		while (1)
		{
			if (x0 + dashLen > x1)
			{
				// draw partial
				surface()->DrawFilledRect(x0, y0, x1, y1);
			}
			else
			{
				surface()->DrawFilledRect(x0, y0, x0 + dashLen, y1);
			}

			x0 += dashLen;

			if (x0 + gapLen > x1)
				break;

			x0 += gapLen;
		}
	}
	else
	{
		// y direction
		while (1)
		{
			if (y0 + dashLen > y1)
			{
				// draw partial
				surface()->DrawFilledRect(x0, y0, x1, y1);
			}
			else
			{
				surface()->DrawFilledRect(x0, y0, x1, y0 + dashLen);
			}

			y0 += dashLen;

			if (y0 + gapLen > y1)
				break;

			y0 += gapLen;
		}
	}
}

void Label::SetContentAlignment(Alignment alignment)
{
	_contentAlignment=alignment;
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: Size the width of the label to its contents - only works from in ApplySchemeSettings or PerformLayout()
//-----------------------------------------------------------------------------
void Label::SizeToContents()
{
	int wide, tall;
	GetContentSize(wide, tall);

	SetSize(wide, tall);
}

//-----------------------------------------------------------------------------
// Purpose: Set the font the text is drawn in
//-----------------------------------------------------------------------------
void Label::SetFont(HFont font)
{
	_textImage->SetFont(font);
	Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: Resond to resizing of the panel
//-----------------------------------------------------------------------------
void Label::OnSizeChanged(int wide, int tall)
{
	InvalidateLayout();
	Panel::OnSizeChanged(wide, tall);
}

//-----------------------------------------------------------------------------
// Purpose: Get the font the textImage is drawn in.
//-----------------------------------------------------------------------------
HFont Label::GetFont()
{
	return _textImage->GetFont();
}

//-----------------------------------------------------------------------------
// Purpose: Set the foreground color of the Label
//-----------------------------------------------------------------------------
void Label::SetFgColor(Color color)
{
	if (!(GetFgColor() == color))
	{
		BaseClass::SetFgColor(color);
		_textImage->SetColor(color);
		Repaint();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Get the foreground color of the Label
//-----------------------------------------------------------------------------
Color Label::GetFgColor()
{
	Color clr = Panel::GetFgColor();
	return clr;
}

//-----------------------------------------------------------------------------
// Purpose: Set the foreground color 1 color of the Label
//-----------------------------------------------------------------------------
void Label::SetDisabledFgColor1(Color color)
{
	_disabledFgColor1 = color;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Label::SetDisabledFgColor2(Color color)
{
	_disabledFgColor2 = color;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
Color Label::GetDisabledFgColor1()
{
	return _disabledFgColor1;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
Color Label::GetDisabledFgColor2()
{
	return _disabledFgColor2;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
TextImage *Label::GetTextImage()
{
	return _textImage;
}


//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
bool Label::RequestInfo(KeyValues *outputData)
{
	if (!stricmp(outputData->GetName(), "GetText"))
	{
		wchar_t wbuf[256];
		_textImage->GetText(wbuf, 255);
		outputData->SetWString("text", wbuf);
		return true;
	}

	return Panel::RequestInfo(outputData);
}

//-----------------------------------------------------------------------------
// Purpose: Sets the text from the message
//-----------------------------------------------------------------------------
void Label::OnSetText(KeyValues *params)
{
	KeyValues *pkvText = params->FindKey("text", false);
	if (!pkvText)
		return;

	if (pkvText->GetDataType() == KeyValues::TYPE_STRING)
	{
		SetText(pkvText->GetString());
	}
	else if (pkvText->GetDataType() == KeyValues::TYPE_WSTRING)
	{
		SetText(pkvText->GetWString());
	}
}

//-----------------------------------------------------------------------------
// Purpose: Add an image to the list
//			returns the index the image was placed in
//-----------------------------------------------------------------------------
int Label::AddImage(IImage *image, int offset)
{
	int newImage = _imageDar.AddToTail();
	_imageDar[newImage].image = image;
	_imageDar[newImage].offset = (short)offset;
	_imageDar[newImage].xpos = -1;
	_imageDar[newImage].width = -1;
	InvalidateLayout();
	return newImage;
}

//-----------------------------------------------------------------------------
// Purpose: removes all images from the list
//			user is responsible for the memory
//-----------------------------------------------------------------------------
void Label::ClearImages()
{
	_imageDar.RemoveAll();
	_textImageIndex = -1;
}

void Label::ResetToSimpleTextImage()
{
	ClearImages();
	_textImageIndex = AddImage(_textImage, 0);
}


//-----------------------------------------------------------------------------
// Purpose: Multiple image handling
//			Images are drawn from left to right across the label, ordered by index
//			By default there is a TextImage in position 0
//			Set the contents of an IImage in the IImage array.
//-----------------------------------------------------------------------------
void Label::SetImageAtIndex(int index, IImage *image, int offset)
{
	EnsureImageCapacity(index);
//	Assert( image );

	if ( _imageDar[index].image != image || _imageDar[index].offset != offset)
	{
		_imageDar[index].image = image;
		_imageDar[index].offset = (short)offset;
		InvalidateLayout();
	}
}

//-----------------------------------------------------------------------------
// Purpose: Get an IImage in the IImage array.
//-----------------------------------------------------------------------------
IImage *Label::GetImageAtIndex(int index)
{
	if ( _imageDar.IsValidIndex( index ) )
		return _imageDar[index].image;
	return NULL;
}

//-----------------------------------------------------------------------------
// Purpose: Get the number of images in the array.
//-----------------------------------------------------------------------------
int Label::GetImageCount()
{
	return _imageDar.Count();
}

//-----------------------------------------------------------------------------
// Purpose: Move where the default text image is within the image array 
//			(it starts in position 0)
// Input  : newIndex - 
// Output : int - the index the default text image was previously in
//-----------------------------------------------------------------------------
int Label::SetTextImageIndex(int newIndex)
{
	if (newIndex == _textImageIndex)
		return _textImageIndex;

	EnsureImageCapacity(newIndex);

	int oldIndex = _textImageIndex;
	if ( _textImageIndex >= 0 )
	{
		_imageDar[_textImageIndex].image = NULL;
	}
	if (newIndex > -1)
	{
		_imageDar[newIndex].image = _textImage;
	}
	_textImageIndex = newIndex;
	return oldIndex;
}

//-----------------------------------------------------------------------------
// Purpose: Ensure that the maxIndex will be a valid index
//-----------------------------------------------------------------------------
void Label::EnsureImageCapacity(int maxIndex)
{
	while (_imageDar.Size() <= maxIndex)
	{
		AddImage(NULL, 0);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Set the offset in pixels before the image
//-----------------------------------------------------------------------------
void Label::SetImagePreOffset(int index, int preOffset)
{
	if (_imageDar.IsValidIndex(index) && _imageDar[index].offset != preOffset)
	{
		_imageDar[index].offset = (short)preOffset;
		InvalidateLayout();
	}
}

//-----------------------------------------------------------------------------
// Purpose: fixes the layout bounds of the image within the label
//-----------------------------------------------------------------------------
void Label::SetImageBounds(int index, int x, int width)
{
	_imageDar[index].xpos = (short)x;
	_imageDar[index].width = (short)width;
}

//-----------------------------------------------------------------------------
// Purpose: Labels can be associated with controls, and alter behaviour based on the associates behaviour
//			If the associate is disabled, so are we
//			If the associate has focus, we may alter how we draw
//			If we get a hotkey press or focus message, we forward the focus to the associate
//-----------------------------------------------------------------------------
void Label::SetAssociatedControl(Panel *control)
{
	if (control != this)
	{
		_associate = control;
	}
	else
	{
		// don't let the associate ever be set to be ourself
		_associate = NULL;
	}
}

//-----------------------------------------------------------------------------
// Purpose: Called after a panel requests focus to fix up the whole chain
//-----------------------------------------------------------------------------
void Label::OnRequestFocus(VPANEL subFocus, VPANEL defaultPanel)
{
	if (_associate.Get() && subFocus == GetVPanel() && !IsBuildModeActive())
	{
		// we've received focus; pass the focus onto the associate instead
		_associate->RequestFocus();
	}
	else
	{
		BaseClass::OnRequestFocus(subFocus, defaultPanel);
	}
}

//-----------------------------------------------------------------------------
// Purpose: sets custom settings from the scheme file
//-----------------------------------------------------------------------------
void Label::ApplySchemeSettings(IScheme *pScheme)
{
	BaseClass::ApplySchemeSettings(pScheme);

	if (_fontOverrideName)
	{
		// use the custom specified font since we have one set
		SetFont(pScheme->GetFont(_fontOverrideName, IsProportional()));
	}
	if ( GetFont() == INVALID_FONT )
	{
		SetFont( pScheme->GetFont( "Default", IsProportional() ) );
	}	

	if ( m_bWrap || m_bCenterWrap )
	{
		//tell it how big it is
		int wide, tall;
		Panel::GetSize(wide, tall);
		wide -= _textInset[0];		// take inset into account
		_textImage->SetSize(wide, tall);

		_textImage->RecalculateNewLinePositions();
	}
	else
	{
		// if you don't set the size of the image, many, many buttons will break - we might want to look into fixing this all over the place later
		int wide, tall;
		_textImage->GetContentSize(wide, tall);
		_textImage->SetSize(wide, tall);
	}

	if ( m_bAutoWideToContents )
	{
		m_bAutoWideDirty = true;
		HandleAutoSizing();
	}

	// clear out any the images, since they will have been invalidated
	for (int i = 0; i < _imageDar.Count(); i++)
	{
		IImage *image = _imageDar[i].image;
		if (!image)
			continue; // skip over null images

		if (i == _textImageIndex)
			continue;

		_imageDar[i].image = NULL;
	}

	SetDisabledFgColor1(GetSchemeColor("Label.DisabledFgColor1", pScheme));
	SetDisabledFgColor2(GetSchemeColor("Label.DisabledFgColor2", pScheme));
	SetBgColor(GetSchemeColor("Label.BgColor", pScheme));

	switch (_textColorState)
	{
	case CS_DULL:
		SetFgColor(GetSchemeColor("Label.TextDullColor", pScheme));
		break;
	case CS_BRIGHT:
		SetFgColor(GetSchemeColor("Label.TextBrightColor", pScheme));
		break;
	case CS_NORMAL:
	default:
		SetFgColor(GetSchemeColor("Label.TextColor", pScheme));
		break;
	}

	_associateColor = GetSchemeColor("Label.SelectedTextColor", pScheme);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Label::GetSettings( KeyValues *outResourceData )
{
	// panel settings
	Panel::GetSettings( outResourceData );

	// label settings
	char buf[256];
	_textImage->GetUnlocalizedText( buf, 255 );
	if (!strnicmp(buf, "#var_", 5))
	{
		// strip off the variable prepender on save
		outResourceData->SetString( "labelText", buf + 5 );
	}
	else
	{
		outResourceData->SetString( "labelText", buf );
	}

	const char *alignmentString = "";
	switch ( _contentAlignment )
	{
	case a_northwest:	alignmentString = "north-west";	break;
	case a_north:		alignmentString = "north";		break;
	case a_northeast:	alignmentString = "north-east";	break;
	case a_center:		alignmentString = "center";		break;
	case a_east:		alignmentString = "east";		break;
	case a_southwest:	alignmentString = "south-west";	break;
	case a_south:		alignmentString = "south";		break;
	case a_southeast:	alignmentString = "south-east";	break;
	case a_west:	
	default:			alignmentString = "west";	break;
	}

	outResourceData->SetString( "textAlignment", alignmentString );

	if (_associate)
	{
		outResourceData->SetString("associate", _associate->GetName());
	}

	outResourceData->SetInt("dulltext", (int)(_textColorState == CS_DULL));
	outResourceData->SetInt("brighttext", (int)(_textColorState == CS_BRIGHT));

	if (_fontOverrideName)
	{
		outResourceData->SetString("font", _fontOverrideName);
	}
	
	outResourceData->SetInt("wrap", ( m_bWrap ? 1 : 0 ));
	outResourceData->SetInt("centerwrap", ( m_bCenterWrap ? 1 : 0 ));

	if ( m_bUseProportionalInsets )
	{
		outResourceData->SetInt("textinsetx", scheme()->GetProportionalNormalizedValueEx( GetScheme(), _textInset[0] ) );
		outResourceData->SetInt("textinsety", _textInset[1]);
	}
	else
	{
		outResourceData->SetInt("textinsetx", _textInset[0]);
		outResourceData->SetInt("textinsety", _textInset[1]);
	}
	outResourceData->SetInt("auto_wide_tocontents", ( m_bAutoWideToContents ? 1 : 0 ));
	outResourceData->SetInt("use_proportional_insets", ( m_bUseProportionalInsets ? 1 : 0 ));
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void Label::ApplySettings( KeyValues *inResourceData )
{
	BaseClass::ApplySettings( inResourceData );

	// label settings
	const char *labelText =	inResourceData->GetString( "labelText", NULL );
	if ( labelText )
	{
		if (labelText[0] == '%' && labelText[strlen(labelText) - 1] == '%')
		{
			// it's a variable, set it to be a special variable localized string
			wchar_t unicodeVar[256];
			g_pVGuiLocalize->ConvertANSIToUnicode(labelText, unicodeVar, sizeof(unicodeVar));

			char var[256];
			_snprintf(var, sizeof(var), "#var_%s", labelText);
			g_pVGuiLocalize->AddString(var + 1, unicodeVar, "");
			SetText(var);
		}
		else
		{
			SetText(labelText);
		}
	}

	// text alignment
	const char *alignmentString = inResourceData->GetString( "textAlignment", "" );
	int align = -1;

	if ( !stricmp(alignmentString, "north-west") )
	{
		align = a_northwest;
	}
	else if ( !stricmp(alignmentString, "north") )
	{
		align = a_north;
	}
	else if ( !stricmp(alignmentString, "north-east") )
	{
		align = a_northeast;
	}
	else if ( !stricmp(alignmentString, "west") )
	{
		align = a_west;
	}
	else if ( !stricmp(alignmentString, "center") )
	{
		align = a_center;
	}
	else if ( !stricmp(alignmentString, "east") )
	{
		align = a_east;
	}
	else if ( !stricmp(alignmentString, "south-west") )
	{
		align = a_southwest;
	}
	else if ( !stricmp(alignmentString, "south") )
	{
		align = a_south;
	}
	else if ( !stricmp(alignmentString, "south-east") )
	{
		align = a_southeast;
	}

	if ( align != -1 )
	{
		SetContentAlignment( (Alignment)align );
	}

	// the control we are to be associated with may not have been created yet,
	// so keep a pointer to it's name and calculate it when we can
	const char *associateName = inResourceData->GetString("associate", "");
	if (associateName[0] != 0)
	{
		int len = Q_strlen(associateName) + 1;
		_associateName = new char[ len ];
		Q_strncpy( _associateName, associateName, len );
	}

	if (inResourceData->GetInt("dulltext", 0) == 1)
	{
		SetTextColorState(CS_DULL);
	}
	else if (inResourceData->GetInt("brighttext", 0) == 1)
	{
		SetTextColorState(CS_BRIGHT);
	}
	else
	{
		SetTextColorState(CS_NORMAL);
	}

	// font settings
	const char *overrideFont = inResourceData->GetString("font", "");
	IScheme *pScheme = scheme()->GetIScheme( GetScheme() );

	if (*overrideFont)
	{
		delete [] _fontOverrideName;
		int len = Q_strlen(overrideFont) + 1;
		_fontOverrideName = new char[ len ];
		Q_strncpy(_fontOverrideName, overrideFont, len );
		SetFont(pScheme->GetFont(_fontOverrideName, IsProportional()));
	}
	else if (_fontOverrideName)
	{
		delete [] _fontOverrideName;
		_fontOverrideName = NULL;
		SetFont(pScheme->GetFont("Default", IsProportional()));
	}

	bool bWrapText = inResourceData->GetInt("centerwrap", 0) > 0;
	SetCenterWrap( bWrapText );

	m_bAutoWideToContents = inResourceData->GetInt("auto_wide_tocontents", 0) > 0;

	bWrapText = inResourceData->GetInt("wrap", 0) > 0;
	SetWrap( bWrapText );

	int inset_x = inResourceData->GetInt("textinsetx", _textInset[0]);
	int inset_y = inResourceData->GetInt("textinsety", _textInset[1]);
	// Had to play it safe and add a new key for backwards compatibility
	m_bUseProportionalInsets = inResourceData->GetInt("use_proportional_insets", 0) > 0;
	if ( m_bUseProportionalInsets )
	{
		inset_x = scheme()->GetProportionalScaledValueEx( GetScheme(), inset_x );
	}

	SetTextInset( inset_x, inset_y );

	bool bAllCaps = inResourceData->GetInt("allcaps", 0) > 0;
	SetAllCaps( bAllCaps );

	InvalidateLayout(true);
}

//-----------------------------------------------------------------------------
// Purpose: Returns a description of the label string
//-----------------------------------------------------------------------------
const char *Label::GetDescription( void )
{
	static char buf[1024];
	Q_snprintf(buf, sizeof(buf), "%s, string labelText, string associate, alignment textAlignment, int wrap, int dulltext, int brighttext, string font", BaseClass::GetDescription());
	return buf;
}

//-----------------------------------------------------------------------------
// Purpose: If a label has images in _imageDar, the size
//			must take those into account as well as the textImage part
//			Textimage part will shrink ONLY if there is not enough room.
//-----------------------------------------------------------------------------
void Label::PerformLayout()
{
	int wide, tall;
	Panel::GetSize(wide, tall);
	wide -= _textInset[0]; // take inset into account

	// if we just have a textImage, this is trivial.
	if (_imageDar.Count() == 1 && _textImageIndex == 0)
	{	
		if ( m_bWrap || m_bCenterWrap )
		{
			int twide, ttall;
			_textImage->GetContentSize(twide, ttall);
			_textImage->SetSize(wide, ttall);
		}
		else
		{
			int twide, ttall;
			_textImage->GetContentSize(twide, ttall);
			
			// tell the textImage how much space we have to draw in
			if ( wide < twide)
				_textImage->SetSize(wide, ttall);
			else
				_textImage->SetSize(twide, ttall);
		}

		HandleAutoSizing();

		HandleAutoSizing();

		return;
	}

	// assume the images in the dar cannot be resized, and if
	// the images + the textimage are too wide we shring the textimage part
	if (_textImageIndex < 0)
		return;
	
	// get the size of the images
	int	widthOfImages = 0;
	for (int i = 0; i < _imageDar.Count(); i++)
	{
		TImageInfo &imageInfo = _imageDar[i];
		IImage *image = imageInfo.image;
		if (!image)
			continue; // skip over null images

		if (i == _textImageIndex)
			continue;

		// add up the bounds
		int iWide, iTall;
		image->GetSize(iWide, iTall);		
		widthOfImages += iWide;
	}

	// so this is how much room we have to draw the textimage part
	int spaceAvail = wide - widthOfImages;

	// if we have no space at all just leave everything as is.
	if (spaceAvail < 0)
		return;

	int twide, ttall;
	_textImage->GetSize (twide, ttall);
	// tell the textImage how much space we have to draw in
	_textImage->SetSize(spaceAvail, ttall);	

	HandleAutoSizing();
}

void Label::SetWrap( bool bWrap )
{
	m_bWrap = bWrap;
	_textImage->SetWrap( m_bWrap );

	InvalidateLayout();
}

void Label::SetCenterWrap( bool bWrap )
{
	m_bCenterWrap = bWrap;
	_textImage->SetCenterWrap( m_bCenterWrap );

	InvalidateLayout();
}

void Label::SetAllCaps( bool bAllCaps )
{
	m_bAllCaps = bAllCaps;
	_textImage->SetAllCaps( m_bAllCaps );

	InvalidateLayout();
}

void Label::HandleAutoSizing( void )
{
	if ( m_bAutoWideDirty )
	{
		m_bAutoWideDirty = false;

		// Only change our width to match our content
		int wide, tall;
		GetContentSize(wide, tall);
		SetSize(wide, GetTall());
	}
}


//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: 
//
// $NoKeywords: $
//=============================================================================//

#include <assert.h>

#include <vgui/IScheme.h>
#include <vgui/ISystem.h>
#include <vgui/IInput.h>
#include <vgui/IImage.h>
#include <KeyValues.h>

#include <vgui_controls/ScrollBar.h>
#include <vgui_controls/ScrollBarSlider.h>
#include <vgui_controls/Button.h>
#include <vgui_controls/Controls.h>
#include <vgui_controls/ImagePanel.h>

// memdbgon must be the last include file in a .cpp file!!!
#include <tier0/memdbgon.h>

using namespace vgui;

namespace
{

enum
{						 // scroll bar will scroll a little, then continuous scroll like in windows
	SCROLL_BAR_DELAY = 400,	 // default delay for all scroll bars
	SCROLL_BAR_SPEED = 50, // this is how fast the bar scrolls when you hold down the arrow button
	SCROLLBAR_DEFAULT_WIDTH = 17,
};

//-----------------------------------------------------------------------------
// Purpose: Scroll bar button-the arrow button that moves the slider up and down.
//-----------------------------------------------------------------------------
class ScrollBarButton : public Button
{
public:
	ScrollBarButton(Panel *parent, const char *panelName, const char *text) : Button(parent, panelName, text)
	{
		SetButtonActivationType(ACTIVATE_ONPRESSED);

		SetContentAlignment(Label::a_center);
	}

	void OnMouseFocusTicked()
	{
		// pass straight up to parent
		CallParentFunction(new KeyValues("MouseFocusTicked"));
	}
 
	virtual void ApplySchemeSettings(IScheme *pScheme)
	{
		Button::ApplySchemeSettings(pScheme);

		SetFont(pScheme->GetFont("Marlett", IsProportional() ));
		SetDefaultBorder(pScheme->GetBorder("ScrollBarButtonBorder"));
        SetDepressedBorder(pScheme->GetBorder("ScrollBarButtonDepressedBorder"));
		
		SetDefaultColor(GetSchemeColor("ScrollBarButton.FgColor", pScheme), GetSchemeColor("ScrollBarButton.BgColor", pScheme));
		SetArmedColor(GetSchemeColor("ScrollBarButton.ArmedFgColor", pScheme), GetSchemeColor("ScrollBarButton.ArmedBgColor", pScheme));
		SetDepressedColor(GetSchemeColor("ScrollBarButton.DepressedFgColor", pScheme), GetSchemeColor("ScrollBarButton.DepressedBgColor", pScheme));
	}

	// Don't request focus.
	// This will keep cursor focus in main window in text entry windows.
	virtual void OnMousePressed(MouseCode code)
	{
		if (!IsEnabled())
			return;
		
		if (!IsMouseClickEnabled(code))
			return;
		
		if (IsUseCaptureMouseEnabled())
		{
			{
				SetSelected(true);
				Repaint();
			}
			
			// lock mouse input to going to this button
			input()->SetMouseCapture(GetVPanel());
		}
	}
    virtual void OnMouseReleased(MouseCode code)
    {
		if (!IsEnabled())
			return;
		
		if (!IsMouseClickEnabled(code))
			return;
		
		if (IsUseCaptureMouseEnabled())
		{
			{
				SetSelected(false);
				Repaint();
			}
			
			// lock mouse input to going to this button
			input()->SetMouseCapture(NULL);
		}

		if( input()->GetMouseOver() == GetVPanel() )
		{
			SetArmed( true );
		}
    }

};

}

vgui::Panel *ScrollBar_Vertical_Factory()
{
	return new ScrollBar(NULL, NULL, true );
}

vgui::Panel *ScrollBar_Horizontal_Factory()
{
	return new ScrollBar(NULL, NULL, false );
}

DECLARE_BUILD_FACTORY_CUSTOM_ALIAS( ScrollBar, ScrollBar_Vertical, ScrollBar_Vertical_Factory );
DECLARE_BUILD_FACTORY_CUSTOM_ALIAS( ScrollBar, ScrollBar_Horizontal, ScrollBar_Horizontal_Factory );
// Default is a horizontal one
DECLARE_BUILD_FACTORY_CUSTOM( ScrollBar, ScrollBar_Horizontal_Factory );

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
ScrollBar::ScrollBar(Panel *parent, const char *panelName, bool vertical) : Panel(parent, panelName)
{
	_slider=null;
	_button[0]=null;
	_button[1]=null;
	_scrollDelay = SCROLL_BAR_DELAY;
	_respond = true;
	m_pUpArrow = NULL;
	m_pLine = NULL;
	m_pDownArrow = NULL;
	m_pBox = NULL;
	m_bNoButtons = false;
	m_pOverriddenButtons[0] = NULL;
	m_pOverriddenButtons[1] = NULL;

	if (vertical)
	{
		// FIXME: proportional changes needed???
		SetSlider(new ScrollBarSlider(NULL, "Slider", true));
		SetButton(new ScrollBarButton(NULL, "UpButton", "t"), 0);
		SetButton(new ScrollBarButton(NULL, "DownButton", "u"), 1);
		_button[0]->SetTextInset(0, 1);
		_button[1]->SetTextInset(0, -1);

		SetSize(SCROLLBAR_DEFAULT_WIDTH, 64);
	}
	else
	{
		SetSlider(new ScrollBarSlider(NULL, NULL, false));
		SetButton(new ScrollBarButton(NULL, NULL, "w"), 0);
		SetButton(new ScrollBarButton(NULL, NULL, "4"), 1);
		_button[0]->SetTextInset(0, 0);
		_button[1]->SetTextInset(0, 0);

		SetSize(64, SCROLLBAR_DEFAULT_WIDTH);
	}

	Panel::SetPaintBorderEnabled(true);
	Panel::SetPaintBackgroundEnabled(false);
	Panel::SetPaintEnabled(true);
	SetButtonPressedScrollValue(20);
	SetBlockDragChaining( true );

	Validate();
}

//-----------------------------------------------------------------------------
// Purpose: sets up the width of the scrollbar according to the scheme
//-----------------------------------------------------------------------------
void ScrollBar::ApplySchemeSettings(IScheme *pScheme)
{
	BaseClass::ApplySchemeSettings(pScheme);

	const char *resourceString = pScheme->GetResourceString("ScrollBar.Wide");

	if (resourceString)
	{
		int value = atoi(resourceString);
		if (IsProportional())
		{
			value = scheme()->GetProportionalScaledValueEx(GetScheme(), value);
		}

		if (_slider && _slider->IsVertical())
		{
			// we're vertical, so reset the width
			SetSize( value, GetTall() );
		}
		else
		{
			// we're horizontal, so the width means the height
			SetSize( GetWide(), value );
		}
	}

	UpdateButtonsForImages();
}

//-----------------------------------------------------------------------------
// Purpose: Set the slider's Paint border enabled.
//-----------------------------------------------------------------------------
void ScrollBar::SetPaintBorderEnabled(bool state)
{
	if ( _slider )
	{
		_slider->SetPaintBorderEnabled( state );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ScrollBar::SetPaintBackgroundEnabled(bool state)
{
	if ( _slider )
	{
		_slider->SetPaintBackgroundEnabled( state );
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ScrollBar::SetPaintEnabled(bool state)
{
	if ( _slider )
	{
		_slider->SetPaintEnabled( state );
	}
}

//-----------------------------------------------------------------------------
// Purpose: Layout the scroll bar and buttons on screen
//-----------------------------------------------------------------------------
void ScrollBar::PerformLayout()
{
	if (_slider)
	{
		int wide, tall;
		GetPaintSize(wide,tall);
		if(_slider->IsVertical())
		{
			if ( m_bNoButtons )
			{
				_slider->SetBounds(0, 0, wide, tall + 1);
			}
			else
			{
				_slider->SetBounds(0, wide, wide, tall-(wide*2)+1);
				_button[0]->SetBounds(0,0, wide, wide );
				_button[1]->SetBounds(0,tall-wide ,wide, wide );
			}
		}
		else
		{
			if ( m_bNoButtons )
			{
				_slider->SetBounds(tall, 0, wide, tall + 1);
			}
			else
			{
				_slider->SetBounds(tall, -1, wide-(tall*2)+1, tall + 1 );
				_button[0]->SetBounds(0, 0, tall, tall);
				_button[1]->SetBounds(wide-tall, 0, tall, tall);
			}
		}

		// Place the images over the appropriate controls
		int x,y;
		if ( m_pUpArrow )
		{
			_button[0]->GetBounds( x,y,wide,tall );
			m_pUpArrow->SetBounds( x,y,wide,tall );
		}
		if ( m_pDownArrow )
		{
			_button[1]->GetBounds( x,y,wide,tall );
			m_pDownArrow->SetBounds( x,y,wide,tall );
		}
		if ( m_pLine )
		{
			_slider->GetBounds( x,y,wide,tall );
			m_pLine->SetBounds( x,y,wide,tall );
		}
		if ( m_pBox )
		{
			m_pBox->SetBounds( 0, wide, wide, wide );
		}

		_slider->MoveToFront();
		// after resizing our child, we should remind it to perform a layout
		_slider->InvalidateLayout();

		UpdateSliderImages();
	}

	if ( m_bAutoHideButtons )
	{
		SetScrollbarButtonsVisible( _slider->IsSliderVisible() );
	}

	// get tooltips to draw
	Panel::PerformLayout();
}

//-----------------------------------------------------------------------------
// Purpose: Set the value of the scroll bar slider.
//-----------------------------------------------------------------------------
void ScrollBar::SetValue(int value)
{
	_slider->SetValue(value);
}

//-----------------------------------------------------------------------------
// Purpose: Get the value of the scroll bar slider.
//-----------------------------------------------------------------------------
int ScrollBar::GetValue()
{
	return _slider->GetValue();
}

//-----------------------------------------------------------------------------
// Purpose: Set the range of the scroll bar slider.
// This the range of numbers the slider can scroll through.
//-----------------------------------------------------------------------------
void ScrollBar::SetRange(int min,int max)
{
	_slider->SetRange(min,max);
}

//-----------------------------------------------------------------------------
// Purpose: Gets the range of the scroll bar slider.
// This the range of numbers the slider can scroll through.
//-----------------------------------------------------------------------------
void ScrollBar::GetRange(int &min, int &max)
{
    _slider->GetRange(min, max);
}

//-----------------------------------------------------------------------------
// Purpose: Send a message when the slider is moved.
// Input  : value - 
//-----------------------------------------------------------------------------
void ScrollBar::SendSliderMoveMessage(int value)
{
	PostActionSignal(new KeyValues("ScrollBarSliderMoved", "position", value));
}

//-----------------------------------------------------------------------------
// Purpose: Called when the Slider is dragged by the user
// Input  : value - 
//-----------------------------------------------------------------------------
void ScrollBar::OnSliderMoved(int value)
{
	SendSliderMoveMessage(value);
	UpdateSliderImages();
}

//-----------------------------------------------------------------------------
// Purpose: Check if the scrollbar is vertical (true) or horizontal (false)
//-----------------------------------------------------------------------------
bool ScrollBar::IsVertical()
{
	return _slider->IsVertical();
}

//-----------------------------------------------------------------------------
// Purpose: Check if the the scrollbar slider has full range.
// Normally if you have a scroll bar and the range goes from a to b and
// the slider is sized to c, the range will go from a to b-c.
// This makes it so the slider goes from a to b fully.
//-----------------------------------------------------------------------------
bool ScrollBar::HasFullRange()
{
	return _slider->HasFullRange();
}

//-----------------------------------------------------------------------------
// Purpose: Setup the indexed scroll bar button with the input params.
//-----------------------------------------------------------------------------
//LEAK: new and old slider will leak
void ScrollBar::SetButton(Button *button, int index)
{
	if(_button[index]!=null)
	{
		_button[index]->SetParent((Panel *)NULL);
	}
	_button[index]=button;
	_button[index]->SetParent(this);
	_button[index]->AddActionSignalTarget(this);
	_button[index]->SetCommand(new KeyValues("ScrollButtonPressed", "index", index));

	Validate();
}


//-----------------------------------------------------------------------------
// Purpose: Return the indexed scroll bar button
//-----------------------------------------------------------------------------
Button* ScrollBar::GetButton(int index)
{
	return _button[index];
}


//-----------------------------------------------------------------------------
// Purpose: Set up the slider.
//-----------------------------------------------------------------------------
//LEAK: new and old slider will leak
void ScrollBar::SetSlider(ScrollBarSlider *slider)
{
	if(_slider!=null)
	{
		_slider->SetParent((Panel *)NULL);
	}
	_slider=slider;
	_slider->AddActionSignalTarget(this);
	_slider->SetParent(this);

	Validate();
}

//-----------------------------------------------------------------------------
// Purpose: Return a pointer to the slider.
//-----------------------------------------------------------------------------
ScrollBarSlider *ScrollBar::GetSlider()
{
	return _slider;
}

Button *ScrollBar::GetDepressedButton( int iIndex )
{
	if ( iIndex == 0 )
		return ( m_pOverriddenButtons[0] ? m_pOverriddenButtons[0] : _button[0] );
	return ( m_pOverriddenButtons[1] ? m_pOverriddenButtons[1] : _button[1] );
}

//-----------------------------------------------------------------------------
// Purpose: Scrolls in response to clicking and holding on up or down arrow
// The idea is to have the slider move one step then delay a bit and then
// the bar starts moving at normal speed. This gives a stepping feeling
// to just clicking an arrow once.
//-----------------------------------------------------------------------------
void ScrollBar::OnMouseFocusTicked()
{
	int direction = 0;
	
	// top button is down
	if ( GetDepressedButton(0)->IsDepressed() )
	{
		direction = -1;
	}
	// bottom top button is down
	else if (GetDepressedButton(1)->IsDepressed())
	{
		direction = 1;
	}

	// a button is down 
	if ( direction != 0 )  
	{
		RespondToScrollArrow(direction);
		if (_scrollDelay < system()->GetTimeMillis())
		{
			_scrollDelay = system()->GetTimeMillis() + SCROLL_BAR_SPEED;
			_respond = true; 
		}
		else
		{
			_respond = false; 
		}		
	}
	// a button is not down.
	else 
	{
		// if neither button is down keep delay at max
		_scrollDelay = system()->GetTimeMillis() + SCROLL_BAR_DELAY;
		_respond = true; 
	}
}

//-----------------------------------------------------------------------------
// Purpose: move scroll bar in response to the first button
// Input: button and direction to move scroll bar when that button is pressed
//			direction can only by +/- 1 
// Output: whether button is down or not
//-----------------------------------------------------------------------------
void ScrollBar::RespondToScrollArrow(int const direction)
{
	if (_respond)
	{
		int newValue = _slider->GetValue() + (direction * _buttonPressedScrollValue);
		_slider->SetValue(newValue);
		SendSliderMoveMessage(newValue);
	}
}


//-----------------------------------------------------------------------------
// Purpose: Trigger layout changes when the window size is changed.
//-----------------------------------------------------------------------------
void ScrollBar::OnSizeChanged(int wide, int tall)
{
	InvalidateLayout();
	_slider->InvalidateLayout();
}

//-----------------------------------------------------------------------------
// Purpose: Set how far the scroll bar slider moves when a scroll bar button is
// pressed.
//-----------------------------------------------------------------------------
void ScrollBar::SetButtonPressedScrollValue(int value)
{
	_buttonPressedScrollValue=value;
}

//-----------------------------------------------------------------------------
// Purpose: Set the range of the rangewindow. This is how many 
// lines are displayed at one time 
// in the window the scroll bar is attached to.
// This also controls the size of the slider, its size is proportional
// to the number of lines displayed / total number of lines.
//-----------------------------------------------------------------------------
void ScrollBar::SetRangeWindow(int rangeWindow)
{
	_slider->SetRangeWindow(rangeWindow);
}

//-----------------------------------------------------------------------------
// Purpose: Get the range of the rangewindow. This is how many 
// lines are displayed at one time 
// in the window the scroll bar is attached to.
// This also controls the size of the slider, its size is proportional
// to the number of lines displayed / total number of lines.
//-----------------------------------------------------------------------------
int ScrollBar::GetRangeWindow()
{
	return _slider->GetRangeWindow();
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void ScrollBar::Validate()
{
	if ( _slider != null )
	{
		int buttonOffset = 0;

		for( int i=0; i<2; i++ )
		{
			if( _button[i] != null )
			{
				if( _button[i]->IsVisible() )
				{
					if( _slider->IsVertical() )
					{					
						buttonOffset += _button[i]->GetTall();
					}
					else
					{
						buttonOffset += _button[i]->GetWide();
					}
				}
			}
		}

		_slider->SetButtonOffset(buttonOffset);
	}
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void ScrollBar::SetScrollbarButtonsVisible(bool visible)
{
	for( int i=0; i<2; i++ )
	{
		if( _button[i] != null )
		{
			_button[i]->SetShouldPaint( visible );
			_button[i]->SetEnabled( visible );
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void ScrollBar::UseImages( const char *pszUpArrow, const char *pszDownArrow, const char *pszLine, const char *pszBox )
{
	if ( pszUpArrow )
	{
		if ( !m_pUpArrow )
		{
			m_pUpArrow = new vgui::ImagePanel( this, "UpArrow" );
			if ( m_pUpArrow )
			{
				m_pUpArrow->SetImage( pszUpArrow );
				m_pUpArrow->SetShouldScaleImage( true );
				m_pUpArrow->SetFgColor( Color( 255, 255, 255, 255 ) );
				m_pUpArrow->SetAlpha( 255 );
				m_pUpArrow->SetZPos( -1 );
			}
		}

		m_pUpArrow->SetImage( pszUpArrow );
		m_pUpArrow->SetRotation( IsVertical() ? ROTATED_UNROTATED : ROTATED_CLOCKWISE_90 );
	}
	else if ( m_pUpArrow )
	{
		m_pUpArrow->DeletePanel();
		m_pUpArrow = NULL;
	}

	if ( pszDownArrow )
	{
		if ( !m_pDownArrow )
		{
			m_pDownArrow = new vgui::ImagePanel( this, "DownArrow" );
			if ( m_pDownArrow )
			{
				m_pDownArrow->SetShouldScaleImage( true );
				m_pDownArrow->SetFgColor( Color( 255, 255, 255, 255 ) );
				m_pDownArrow->SetAlpha( 255 );
				m_pDownArrow->SetZPos( -1 );
			}
		}

		m_pDownArrow->SetImage( pszDownArrow );
		m_pDownArrow->SetRotation( IsVertical() ? ROTATED_UNROTATED : ROTATED_CLOCKWISE_90 );
	}
	else if ( m_pDownArrow )
	{
		m_pDownArrow->DeletePanel();
		m_pDownArrow = NULL;
	}

	if ( pszLine )
	{
		if ( !m_pLine )
		{
			m_pLine = new ImagePanel( this, "Line" );
			if ( m_pLine )
			{
				m_pLine->SetShouldScaleImage( true );
				m_pLine->SetZPos( -1 );
			}
		}

		m_pLine->SetImage( pszLine );
		m_pLine->SetRotation( IsVertical() ? ROTATED_UNROTATED : ROTATED_CLOCKWISE_90 );
	}
	else if ( m_pLine )
	{
		m_pLine->DeletePanel();
		m_pLine = NULL;
	}

	if ( pszBox )
	{
		if ( !m_pBox )
		{
			m_pBox = new ImagePanel( this, "Box" );
			if ( m_pBox )
			{
				m_pBox->SetShouldScaleImage( true );
				m_pBox->SetZPos( -1 );
			}
		}

		m_pBox->SetImage( pszBox );
		m_pBox->SetRotation( IsVertical() ? ROTATED_UNROTATED : ROTATED_CLOCKWISE_90 );
	}
	else if ( m_pBox )
	{
		m_pBox->DeletePanel();
		m_pBox = NULL;
	}

	UpdateButtonsForImages();
	InvalidateLayout();
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void ScrollBar::UpdateButtonsForImages( void )
{
	// Turn off parts of our drawing based on which images we're replacing it with
	if ( m_pUpArrow || m_pDownArrow )
	{
		SetScrollbarButtonsVisible( false );
		_button[0]->SetPaintBorderEnabled( false );
		_button[1]->SetPaintBorderEnabled( false );
		m_bAutoHideButtons = false;
	}
	if ( m_pLine || m_pBox )
	{
		SetPaintBackgroundEnabled( false );
		SetPaintBorderEnabled( false );

		if ( _slider )
		{
			_slider->SetPaintEnabled( false );
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
void ScrollBar::UpdateSliderImages( void )
{
	if ( m_pUpArrow && m_pDownArrow )
	{
		// set the alpha on the up arrow
		int nMin, nMax;
		GetRange( nMin, nMax );
		int nScrollPos = GetValue();
		int nRangeWindow = GetRangeWindow();
		int nBottom = nMax - nRangeWindow;
		if ( nBottom < 0 )
		{
			nBottom = 0;
		}

		// set the alpha on the up arrow
		int nAlpha = ( nScrollPos - nMin <= 0 ) ? 90 : 255;
		m_pUpArrow->SetAlpha( nAlpha );

		// set the alpha on the down arrow
		nAlpha = ( nScrollPos >= nBottom ) ? 90 : 255;
		m_pDownArrow->SetAlpha( nAlpha );
	}

	if ( m_pLine && m_pBox )
	{
		ScrollBarSlider *pSlider = GetSlider();
		if ( pSlider && pSlider->GetRangeWindow() > 0 )
		{
			int x, y, w, t, min, max;
			m_pLine->GetBounds( x, y, w, t );

			// If our slider needs layout, force it to do it now
			if ( pSlider->IsLayoutInvalid() )
			{
				pSlider->InvalidateLayout( true );
			}
			pSlider->GetNobPos( min, max );

			if ( IsVertical() )
			{
				m_pBox->SetBounds( x, y + min, w, ( max - min ) );
			}
			else
			{
				m_pBox->SetBounds( x + min, 0, (max-min), t );
			}
		}
	}
}
void ScrollBar::ApplySettings( KeyValues *pInResourceData )
{
	BaseClass::ApplySettings( pInResourceData );

	m_bNoButtons = pInResourceData->GetBool( "nobuttons", false );

	KeyValues *pSliderKV = pInResourceData->FindKey( "Slider" );
	if ( pSliderKV && _slider )
	{
		_slider->ApplySettings( pSliderKV );
	}

	KeyValues *pDownButtonKV = pInResourceData->FindKey( "DownButton" );
	if ( pDownButtonKV && _button[0] )
	{
		_button[0]->ApplySettings( pDownButtonKV );
	}

	KeyValues *pUpButtonKV = pInResourceData->FindKey( "UpButton" );
	if ( pUpButtonKV && _button[0] )
	{
		_button[1]->ApplySettings( pUpButtonKV );
	}
}

//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: 
//
//=============================================================================//

#include <assert.h>
#include <math.h>
#include <stdio.h>

#include <vgui_controls/AnalogBar.h>
#include <vgui_controls/Controls.h>

#include <vgui/ILocalize.h>
#include <vgui/IScheme.h>
#include <vgui/ISurface.h>
#include <KeyValues.h>

// memdbgon must be the last include file in a .cpp file!!!
#include <tier0/memdbgon.h>

using namespace vgui;

DECLARE_BUILD_FACTORY( AnalogBar );


#define ANALOG_BAR_HOME_SIZE 4
#define ANALOG_BAR_HOME_GAP 2
#define ANALOG_BAR_LESS_TALL ( ANALOG_BAR_HOME_SIZE + ANALOG_BAR_HOME_GAP )


//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
AnalogBar::AnalogBar(Panel *parent, const char *panelName) : Panel(parent, panelName)
{
	_analogValue = 0.0f;
	m_pszDialogVar = NULL;
	SetSegmentInfo( 2, 6 );
	SetBarInset( 0 );
	m_iAnalogValueDirection = PROGRESS_EAST;

	m_fHomeValue = 2.0f;
	m_HomeColor = GetFgColor();
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
AnalogBar::~AnalogBar()
{
	delete [] m_pszDialogVar;
}

//-----------------------------------------------------------------------------
// Purpose: data accessor
//-----------------------------------------------------------------------------
void AnalogBar::SetSegmentInfo( int gap, int width )
{
	_segmentGap = gap;
	_segmentWide = width;
}

//-----------------------------------------------------------------------------
// Purpose: returns the number of segment blocks drawn
//-----------------------------------------------------------------------------
int AnalogBar::GetDrawnSegmentCount()
{
	int wide, tall;
	GetSize(wide, tall);
	int segmentTotal = wide / (_segmentGap + _segmentWide);
	return (int)(segmentTotal * _analogValue);
}

//-----------------------------------------------------------------------------
// Purpose: returns the total number of segment blocks drawn (active and inactive)
//-----------------------------------------------------------------------------
int AnalogBar::GetTotalSegmentCount()
{
	int wide, tall;
	GetSize(wide, tall);
	int segmentTotal = wide / (_segmentGap + _segmentWide);
	return segmentTotal;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void AnalogBar::PaintBackground()
{
	// Don't draw a background
}

void AnalogBar::PaintSegment( int &x, int &y, int tall, int wide, Color color, bool bHome )
{
	switch( m_iAnalogValueDirection )
	{
	case PROGRESS_EAST:
		x += _segmentGap;

		if ( bHome )
		{
			surface()->DrawSetColor( GetHomeColor() );
			surface()->DrawFilledRect(x, y, x + _segmentWide, y + ANALOG_BAR_HOME_SIZE );
			surface()->DrawFilledRect(x, y + tall - (y * 2) - ANALOG_BAR_HOME_SIZE, x + _segmentWide, y + tall - (y * 2) );
		}

		surface()->DrawSetColor( color );
		surface()->DrawFilledRect(x, y + ANALOG_BAR_LESS_TALL, x + _segmentWide, y + tall - (y * 2) - ANALOG_BAR_LESS_TALL );
		x += _segmentWide;
		break;

	case PROGRESS_WEST:
		x -= _segmentGap + _segmentWide;

		if ( bHome )
		{
			surface()->DrawSetColor( GetHomeColor() );
			surface()->DrawFilledRect(x, y, x + _segmentWide, y + ANALOG_BAR_HOME_SIZE );
			surface()->DrawFilledRect(x, y + tall - (y * 2) - ANALOG_BAR_HOME_SIZE, x + _segmentWide, y + tall - (y * 2) );
		}

		surface()->DrawSetColor( color );
		surface()->DrawFilledRect(x, y + ANALOG_BAR_LESS_TALL, x + _segmentWide, y + tall - (y * 2) - ANALOG_BAR_LESS_TALL );
		break;

	case PROGRESS_NORTH:
		y -= _segmentGap + _segmentWide;

		if ( bHome )
		{
			surface()->DrawSetColor( GetHomeColor() );
			surface()->DrawFilledRect(x, y, x + ANALOG_BAR_HOME_SIZE, y + _segmentWide );
			surface()->DrawFilledRect(x + wide - (x * 2) - ANALOG_BAR_HOME_SIZE, y, x + wide - (x * 2), y + _segmentWide );
		}

		surface()->DrawSetColor( color );
		surface()->DrawFilledRect(x + ANALOG_BAR_LESS_TALL, y, x + wide - (x * 2) - ANALOG_BAR_LESS_TALL, y + _segmentWide);
		break;

	case PROGRESS_SOUTH:
		y += _segmentGap;

		if ( bHome )
		{
			surface()->DrawSetColor( GetHomeColor() );
			surface()->DrawFilledRect(x, y, x + ANALOG_BAR_HOME_SIZE, y + _segmentWide );
			surface()->DrawFilledRect(x + wide - (x * 2) - ANALOG_BAR_HOME_SIZE, y, x + wide - (x * 2), y + _segmentWide );
		}

		surface()->DrawSetColor( color );
		surface()->DrawFilledRect(x + ANALOG_BAR_LESS_TALL, y, x + wide - (x * 2) - ANALOG_BAR_LESS_TALL, y + _segmentWide);
		y += _segmentWide;
		break;
	}
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void AnalogBar::Paint()
{
	int wide, tall;
	GetSize(wide, tall);

	// gaps
	int segmentTotal = 0, segmentsDrawn = 0;
	int x = 0, y = 0;

	switch( m_iAnalogValueDirection )
	{
	case PROGRESS_WEST:
		x = wide;
		y = m_iBarInset;
		segmentTotal = wide / (_segmentGap + _segmentWide);
		segmentsDrawn = (int)(segmentTotal * _analogValue + 0.5f);
		break;

	case PROGRESS_EAST:
		x = 0;
		y = m_iBarInset;
		segmentTotal = wide / (_segmentGap + _segmentWide);
		segmentsDrawn = (int)(segmentTotal * _analogValue + 0.5f);
		break;

	case PROGRESS_NORTH:
		x = m_iBarInset;
		y = tall;
		segmentTotal = tall / (_segmentGap + _segmentWide);
		segmentsDrawn = (int)(segmentTotal * _analogValue + 0.5f);
		break;

	case PROGRESS_SOUTH:
		x = m_iBarInset;
		y = 0;
		segmentTotal = tall / (_segmentGap + _segmentWide);
		segmentsDrawn = (int)(segmentTotal * _analogValue + 0.5f);
		break;
	}

	int iHomeIndex = (int)( segmentTotal * m_fHomeValue + 0.5f ) - 1;
	if ( iHomeIndex < 0 )
		iHomeIndex = 0;

	for (int i = 0; i < segmentsDrawn; i++)
		PaintSegment( x, y, tall, wide, GetFgColor(), i == iHomeIndex );

	for (int i = segmentsDrawn; i < segmentTotal; i++)
		PaintSegment( x, y, tall, wide, GetBgColor(), i == iHomeIndex );
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void AnalogBar::SetAnalogValue(float analogValue)
{
	if (analogValue != _analogValue)
	{
		// clamp the analogValue value within the range
		if (analogValue < 0.0f)
		{
			analogValue = 0.0f;
		}
		else if (analogValue > 1.0f)
		{
			analogValue = 1.0f;
		}

		_analogValue = analogValue;
		Repaint();
	}
}

//-----------------------------------------------------------------------------
// Purpose: data accessor
//-----------------------------------------------------------------------------
float AnalogBar::GetAnalogValue()
{
	return _analogValue;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void AnalogBar::ApplySchemeSettings(IScheme *pScheme)
{
	Panel::ApplySchemeSettings(pScheme);

	SetBgColor( Color( 255 - GetFgColor().r(), 255 - GetFgColor().g(), 255 - GetFgColor().b(), GetFgColor().a() ) );
}

//-----------------------------------------------------------------------------
// Purpose: utility function for calculating a time remaining string
//-----------------------------------------------------------------------------
bool AnalogBar::ConstructTimeRemainingString(wchar_t *output, int outputBufferSizeInBytes, float startTime, float currentTime, float currentAnalogValue, float lastAnalogValueUpdateTime, bool addRemainingSuffix)
{
	Assert( outputBufferSizeInBytes >= sizeof(output[0]) );
	Assert(lastAnalogValueUpdateTime <= currentTime);
	output[0] = 0;

	// calculate pre-extrapolation values
	float timeElapsed = lastAnalogValueUpdateTime - startTime;
	float totalTime = timeElapsed / currentAnalogValue;

	// calculate seconds
	int secondsRemaining = (int)(totalTime - timeElapsed);
	if (lastAnalogValueUpdateTime < currentTime)
	{
		// old update, extrapolate
		float analogValueRate = currentAnalogValue / timeElapsed;
		float extrapolatedAnalogValue = analogValueRate * (currentTime - startTime);
		float extrapolatedTotalTime = (currentTime - startTime) / extrapolatedAnalogValue;
		secondsRemaining = (int)(extrapolatedTotalTime - timeElapsed);
	}
	// if there's some time, make sure it's at least one second left
	if ( secondsRemaining == 0 && ( ( totalTime - timeElapsed ) > 0 ) )
	{
		secondsRemaining = 1;
	}

	// calculate minutes
	int minutesRemaining = 0;
	while (secondsRemaining >= 60)
	{
		minutesRemaining++;
		secondsRemaining -= 60;
	}

    char minutesBuf[16];
    Q_snprintf(minutesBuf, sizeof( minutesBuf ), "%d", minutesRemaining);
    char secondsBuf[16];
    Q_snprintf(secondsBuf, sizeof( secondsBuf ), "%d", secondsRemaining);

	if (minutesRemaining > 0)
	{
		wchar_t unicodeMinutes[16];
		g_pVGuiLocalize->ConvertANSIToUnicode(minutesBuf, unicodeMinutes, sizeof( unicodeMinutes ));
		wchar_t unicodeSeconds[16];
		g_pVGuiLocalize->ConvertANSIToUnicode(secondsBuf, unicodeSeconds, sizeof( unicodeSeconds ));

		const char *unlocalizedString = "#vgui_TimeLeftMinutesSeconds";
		if (minutesRemaining == 1 && secondsRemaining == 1)
		{
			unlocalizedString = "#vgui_TimeLeftMinuteSecond";
		}
		else if (minutesRemaining == 1)
		{
			unlocalizedString = "#vgui_TimeLeftMinuteSeconds";
		}
		else if (secondsRemaining == 1)
		{
			unlocalizedString = "#vgui_TimeLeftMinutesSecond";
		}

		char unlocString[64];
		Q_strncpy(unlocString, unlocalizedString,sizeof( unlocString ));
		if (addRemainingSuffix)
		{
			Q_strncat(unlocString, "Remaining", sizeof(unlocString ), COPY_ALL_CHARACTERS);
		}
		g_pVGuiLocalize->ConstructString(output, outputBufferSizeInBytes, g_pVGuiLocalize->Find(unlocString), 2, unicodeMinutes, unicodeSeconds);

	}
	else if (secondsRemaining > 0)
	{
		wchar_t unicodeSeconds[16];
		g_pVGuiLocalize->ConvertANSIToUnicode(secondsBuf, unicodeSeconds, sizeof( unicodeSeconds ));

		const char *unlocalizedString = "#vgui_TimeLeftSeconds";
		if (secondsRemaining == 1)
		{
			unlocalizedString = "#vgui_TimeLeftSecond";
		}
		char unlocString[64];
		Q_strncpy(unlocString, unlocalizedString,sizeof(unlocString));
		if (addRemainingSuffix)
		{
			Q_strncat(unlocString, "Remaining",sizeof(unlocString), COPY_ALL_CHARACTERS);
		}
		g_pVGuiLocalize->ConstructString(output, outputBufferSizeInBytes, g_pVGuiLocalize->Find(unlocString), 1, unicodeSeconds);
	}
	else
	{
		return false;
	}
	return true;
}

//-----------------------------------------------------------------------------
// Purpose: data accessor
//-----------------------------------------------------------------------------
void AnalogBar::SetBarInset( int pixels )
{ 
	m_iBarInset = pixels;
}

//-----------------------------------------------------------------------------
// Purpose: data accessor
//-----------------------------------------------------------------------------
int AnalogBar::GetBarInset( void )
{
	return m_iBarInset;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void AnalogBar::ApplySettings(KeyValues *inResourceData)
{
	_analogValue = inResourceData->GetFloat("analogValue", 0.0f);

	const char *dialogVar = inResourceData->GetString("variable", "");
	if (dialogVar && *dialogVar)
	{
		m_pszDialogVar = new char[strlen(dialogVar) + 1];
		strcpy(m_pszDialogVar, dialogVar);
	}

	BaseClass::ApplySettings(inResourceData);
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void AnalogBar::GetSettings(KeyValues *outResourceData)
{
	BaseClass::GetSettings(outResourceData);
	outResourceData->SetFloat("analogValue", _analogValue );

	if (m_pszDialogVar)
	{
		outResourceData->SetString("variable", m_pszDialogVar);
	}
}

//-----------------------------------------------------------------------------
// Purpose: Returns a string description of the panel fields for use in the UI
//-----------------------------------------------------------------------------
const char *AnalogBar::GetDescription( void )
{
	static char buf[1024];
	_snprintf(buf, sizeof(buf), "%s, string analogValue, string variable", BaseClass::GetDescription());
	return buf;
}

//-----------------------------------------------------------------------------
// Purpose: updates analogValue bar bases on values
//-----------------------------------------------------------------------------
void AnalogBar::OnDialogVariablesChanged(KeyValues *dialogVariables)
{
	if (m_pszDialogVar)
	{
		int val = dialogVariables->GetInt(m_pszDialogVar, -1);
		if (val >= 0.0f)
		{
			SetAnalogValue(val / 100.0f);
		}
	}
}


DECLARE_BUILD_FACTORY( ContinuousAnalogBar );

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
ContinuousAnalogBar::ContinuousAnalogBar(Panel *parent, const char *panelName) : AnalogBar(parent, panelName)
{
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void ContinuousAnalogBar::Paint()
{
	int x = 0, y = 0;
	int wide, tall;
	GetSize(wide, tall);

	surface()->DrawSetColor(GetFgColor());

	switch( m_iAnalogValueDirection )
	{
	case PROGRESS_EAST:
		surface()->DrawFilledRect( x, y, x + (int)( wide * _analogValue ), y + tall );
		break;

	case PROGRESS_WEST:
		surface()->DrawFilledRect( x + (int)( wide * ( 1.0f - _analogValue ) ), y, x + wide, y + tall );
		break;

	case PROGRESS_NORTH:
		surface()->DrawFilledRect( x, y + (int)( tall * ( 1.0f - _analogValue ) ), x + wide, y + tall );
		break;

	case PROGRESS_SOUTH:
		surface()->DrawFilledRect( x, y, x + wide, y + (int)( tall * _analogValue ) );
		break;
	}
}

//========= Copyright Valve Corporation, All rights reserved. ============//
//
// Purpose: 
//
// $NoKeywords: $
//
//=============================================================================//
 //========= Copyright � 1996-2003, Valve LLC, All rights reserved. ============
//
// The copyright to the contents herein is the property of Valve, L.L.C.
// The contents may be used and/or copied only with the written permission of
// Valve, L.L.C., or in accordance with the terms and conditions stipulated in
// the agreement/contract under which the contents have been supplied.
//
// Purpose: 
//
// $NoKeywords: $
//=============================================================================


#include <stdio.h>
#define PROTECTED_THINGS_DISABLE

#include "utldict.h"

#include <vgui/KeyCode.h>
#include <vgui/Cursor.h>
#include <vgui/MouseCode.h>
#include <KeyValues.h>
#include <vgui/IInput.h>
#include <vgui/ISystem.h>
#include <vgui/IVGui.h>
#include <vgui/ISurface.h>

#include <vgui_controls/BuildGroup.h>
#include <vgui_controls/Panel.h>
#include <vgui_controls/PHandle.h>
#include <vgui_controls/Label.h>
#include <vgui_controls/EditablePanel.h>
#include <vgui_controls/MessageBox.h>
#include "filesystem.h"

#if defined( _X360 )
#include "xbox/xbox_win32stubs.h"
#endif

// memdbgon must be the last include file in a .cpp file!!!
#include <tier0/memdbgon.h>

using namespace vgui;

//-----------------------------------------------------------------------------
// Handle table
//-----------------------------------------------------------------------------
IMPLEMENT_HANDLES( BuildGroup, 20 )


//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
BuildGroup::BuildGroup(Panel *parentPanel, Panel *contextPanel)
{
	CONSTRUCT_HANDLE( );

	_enabled=false;
	_snapX=1;
	_snapY=1;
	_cursor_sizenwse = dc_sizenwse;
	_cursor_sizenesw = dc_sizenesw;
	_cursor_sizewe = dc_sizewe;
	_cursor_sizens = dc_sizens;
	_cursor_sizeall = dc_sizeall;
	_currentPanel=null;
	_dragging=false;
	m_pResourceName=NULL;
	m_pResourcePathID = NULL;
	m_hBuildDialog=NULL;
	m_pParentPanel=parentPanel;
	for (int i=0; i<4; ++i)
		_rulerNumber[i] = NULL;
	SetContextPanel(contextPanel);
	_showRulers = false;

}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
BuildGroup::~BuildGroup()
{
	if (m_hBuildDialog)
		delete m_hBuildDialog.Get();
	m_hBuildDialog = NULL;

	delete [] m_pResourceName;
	delete [] m_pResourcePathID;

	for (int i=0; i <4; ++i)
	{
		if (_rulerNumber[i])
		{
			delete _rulerNumber[i];
			_rulerNumber[i]= NULL;
		}
	}
	
	DESTRUCT_HANDLE();
}

//-----------------------------------------------------------------------------
// Purpose: Toggles build mode on/off
// Input  : state - new state
//-----------------------------------------------------------------------------
void BuildGroup::SetEnabled(bool state)
{
	if(_enabled != state)
	{
		_enabled = state;
		_currentPanel = NULL;

		if ( state )
		{
			ActivateBuildDialog();
		}
		else
		{
			// hide the build dialog
			if ( m_hBuildDialog )
			{
				m_hBuildDialog->OnCommand("Close");
			}

			// request focus for our main panel
			m_pParentPanel->RequestFocus();
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose: Check if buildgroup is enabled
//-----------------------------------------------------------------------------
bool BuildGroup::IsEnabled()
{
	return _enabled;
}

//-----------------------------------------------------------------------------
// Purpose: Get the list of panels that are currently selected
//-----------------------------------------------------------------------------
CUtlVector<PHandle> *BuildGroup::GetControlGroup()
{
   return &_controlGroup;
}

//-----------------------------------------------------------------------------
// Purpose:	Check if ruler display is activated
//-----------------------------------------------------------------------------
bool BuildGroup::HasRulersOn()
{
   return _showRulers;
}

//-----------------------------------------------------------------------------
// Purpose:	Toggle ruler display 
//-----------------------------------------------------------------------------
void BuildGroup::ToggleRulerDisplay()
{
	_showRulers = !_showRulers;

	if (_rulerNumber[0] == NULL) // rulers haven't been initialized
	{
		_rulerNumber[0] = new Label(m_pBuildContext, NULL, "");
		_rulerNumber[1] = new Label(m_pBuildContext, NULL, "");
		_rulerNumber[2] = new Label(m_pBuildContext, NULL, "");
		_rulerNumber[3] = new Label(m_pBuildContext, NULL, "");
	}
    SetRulerLabelsVisible(_showRulers);

   m_pBuildContext->Repaint();
}


//-----------------------------------------------------------------------------
// Purpose:	Tobble visibility of ruler number labels
//-----------------------------------------------------------------------------
void BuildGroup::SetRulerLabelsVisible(bool state)
{
	_rulerNumber[0]->SetVisible(state);
	_rulerNumber[1]->SetVisible(state);
	_rulerNumber[2]->SetVisible(state);
	_rulerNumber[3]->SetVisible(state);
}

void BuildGroup::ApplySchemeSettings( IScheme *pScheme )
{
	DrawRulers();
}

//-----------------------------------------------------------------------------
// Purpose:	Draw Rulers on screen if conditions are right
//-----------------------------------------------------------------------------
void BuildGroup::DrawRulers()
{		
	// don't draw if visibility is off
	if (!_showRulers)
	{
		return;
	}
	
	// no drawing if we selected the context panel
	if (m_pBuildContext == _currentPanel)
	{
		SetRulerLabelsVisible(false);
		return;
	}
	else
		SetRulerLabelsVisible(true);
	
	int x, y, wide, tall;
	// get base panel's postition
	m_pBuildContext->GetBounds(x, y, wide, tall);
	m_pBuildContext->ScreenToLocal(x,y);
	
	int cx, cy, cwide, ctall;
	_currentPanel->GetBounds (cx, cy, cwide, ctall);
	
	surface()->PushMakeCurrent(m_pBuildContext->GetVPanel(), false);	
	
	// draw rulers
	surface()->DrawSetColor(255, 255, 255, 255);	// white color
	
	surface()->DrawFilledRect(0, cy, cx, cy+1);           //top horiz left
	surface()->DrawFilledRect(cx+cwide, cy, wide, cy+1);  //top horiz right
	
	surface()->DrawFilledRect(0, cy+ctall-1, cx, cy+ctall);   //bottom horiz left
	surface()->DrawFilledRect(cx+cwide, cy+ctall-1, wide, cy+ctall);   //bottom	 horiz right
	
	surface()->DrawFilledRect(cx,0,cx+1,cy);         //top vert left
	surface()->DrawFilledRect(cx+cwide-1,0, cx+cwide, cy);  //top vert right
	
	surface()->DrawFilledRect(cx,cy+ctall, cx+1, tall); //bottom vert left
	surface()->DrawFilledRect(cx+cwide-1, cy+ctall, cx+cwide, tall); //bottom vert right   
	
	surface()->PopMakeCurrent(m_pBuildContext->GetVPanel());
	
	// now let's put numbers with the rulers
	char textstring[20];
	Q_snprintf (textstring, sizeof( textstring ), "%d", cx);
	_rulerNumber[0]->SetText(textstring);
	int twide, ttall;
	_rulerNumber[0]->GetContentSize(twide,ttall);
	_rulerNumber[0]->SetSize(twide,ttall);
	_rulerNumber[0]->SetPos(cx/2-twide/2, cy-ttall+3);
	
	Q_snprintf (textstring, sizeof( textstring ), "%d", cy);
	_rulerNumber[1]->SetText(textstring);
	_rulerNumber[1]->GetContentSize(twide,ttall);
	_rulerNumber[1]->SetSize(twide,ttall);
	_rulerNumber[1]->GetSize(twide,ttall);
	_rulerNumber[1]->SetPos(cx-twide + 3, cy/2-ttall/2);
	
	Q_snprintf (textstring, sizeof( textstring ), "%d", cy);
	_rulerNumber[2]->SetText(textstring);
	_rulerNumber[2]->GetContentSize(twide,ttall);
	_rulerNumber[2]->SetSize(twide,ttall);
	_rulerNumber[2]->SetPos(cx+cwide+(wide-cx-cwide)/2 - twide/2,  cy+ctall-3);
	
	Q_snprintf (textstring, sizeof( textstring ), "%d", cy);
	_rulerNumber[3]->SetText(textstring);
	_rulerNumber[3]->GetContentSize(twide,ttall);
	_rulerNumber[3]->SetSize(twide,ttall);
	_rulerNumber[3]->SetPos(cx+cwide, cy+ctall+(tall-cy-ctall)/2 - ttall/2);
	
}

//-----------------------------------------------------------------------------
// Purpose: respond to cursor movments
//-----------------------------------------------------------------------------
bool BuildGroup::CursorMoved(int x, int y, Panel *panel)
{
	Assert(panel);

	if ( !m_hBuildDialog.Get() )
	{
		if ( panel->GetParent() )
		{
			EditablePanel *ep = dynamic_cast< EditablePanel * >( panel->GetParent() );
			if ( ep )
			{
				BuildGroup *bg = ep->GetBuildGroup();
				if ( bg && bg != this )
				{
					bg->CursorMoved( x, y, panel );
				}
			}
		}
		return false;
	}

	// no moving uneditable panels
	// commented out because this has issues with panels moving 
	// to front and obscuring other panels
	//if (!panel->IsBuildModeEditable())
	//	return;

	if (_dragging)
	{
		input()->GetCursorPos(x, y);
		
		if (_dragMouseCode == MOUSE_RIGHT)
		{
			int newW = max( 1, _dragStartPanelSize[ 0 ] + x - _dragStartCursorPos[0] );
			int newH = max( 1, _dragStartPanelSize[ 1 ] + y - _dragStartCursorPos[1] );

			bool shift = ( input()->IsKeyDown(KEY_LSHIFT) || input()->IsKeyDown(KEY_RSHIFT) );
			bool ctrl = ( input()->IsKeyDown(KEY_LCONTROL) || input()->IsKeyDown(KEY_RCONTROL) );

			if ( shift )
			{
				newW = _dragStartPanelSize[ 0 ];
			}
			if ( ctrl )
			{
				newH = _dragStartPanelSize[ 1 ];
			}

			panel->SetSize( newW, newH );
			ApplySnap(panel);
		}
		else
		{
			for (int i=0; i < _controlGroup.Count(); ++i)
			{
				// now fix offset of member panels with respect to the one we are dragging
				Panel *groupMember = _controlGroup[i].Get();
			   	groupMember->SetPos(_dragStartPanelPos[0] + _groupDeltaX[i] +(x-_dragStartCursorPos[0]), _dragStartPanelPos[1] + _groupDeltaY[i] +(y-_dragStartCursorPos[1]));
				ApplySnap(groupMember);				
			}
		}

		// update the build dialog
		if (m_hBuildDialog)
		{
			KeyValues *keyval = new KeyValues("UpdateControlData");
			keyval->SetPtr("panel", GetCurrentPanel());
			ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), keyval, NULL);

			keyval = new KeyValues("EnableSaveButton");	
			ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), keyval, NULL);	
		}
		
		panel->Repaint();
		panel->CallParentFunction(new KeyValues("Repaint"));
	}

	return true;
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
bool BuildGroup::MousePressed(MouseCode code, Panel *panel)
{
	Assert(panel);

	if ( !m_hBuildDialog.Get() )
	{
		if ( panel->GetParent() )
		{
			EditablePanel *ep = dynamic_cast< EditablePanel * >( panel->GetParent() );
			if ( ep )
			{
				BuildGroup *bg = ep->GetBuildGroup();
				if ( bg && bg != this )
				{
					bg->MousePressed( code, panel );
				}
			}
		}
		return false;
	}

	// if people click on the base build dialog panel.
	if (panel == m_hBuildDialog)
	{
		// hide the click menu if its up
		ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("HideNewControlMenu"), NULL);
		return true;
	}

	// don't select unnamed items
	if (strlen(panel->GetName()) < 1)
		return true;
	
	bool shift = ( input()->IsKeyDown(KEY_LSHIFT) || input()->IsKeyDown(KEY_RSHIFT) );	
	if (!shift)
	{
		_controlGroup.RemoveAll();	
	}

	// Show new ctrl menu if they click on the bg (not on a subcontrol)
	if ( code == MOUSE_RIGHT && panel == GetContextPanel())
	{		
		// trigger a drop down menu to create new controls
		ivgui()->PostMessage (m_hBuildDialog->GetVPanel(), new KeyValues("ShowNewControlMenu"), NULL);	
	}	
	else
	{	
		// don't respond if we click on ruler numbers
		if (_showRulers) // rulers are visible
		{
			for ( int i=0; i < 4; i++)
			{
				if ( panel == _rulerNumber[i])
					return true;
			}
		}

		_dragging = true;
		_dragMouseCode = code;
		ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("HideNewControlMenu"), NULL);
		
		int x, y;
		input()->GetCursorPos(x, y);
		
		_dragStartCursorPos[0] = x;
		_dragStartCursorPos[1] = y;
	
		
		input()->SetMouseCapture(panel->GetVPanel());
		
		_groupDeltaX.RemoveAll();
		_groupDeltaY.RemoveAll();

		// basepanel is the panel that all the deltas will be calculated from.
		// it is the last panel we clicked in because if we move the panels  as a group
		// it would be from that one
		Panel *basePanel = NULL;
		// find the panel we clicked in, that is the base panel
		// it might already be in the group
		for (int i=0; i< _controlGroup.Count(); ++i)	
		{
			if (panel == _controlGroup[i].Get())
			{
				basePanel = panel;
				break;
			}
		}

		// if its not in the group we just added this panel. get it in the group 
		if (basePanel == NULL)
		{
			PHandle temp;
			temp = panel;
			_controlGroup.AddToTail(temp);
			basePanel = panel;
		}
		
		basePanel->GetPos(x,y);
		_dragStartPanelPos[0]=x;
		_dragStartPanelPos[1]=y;

		basePanel->GetSize( _dragStartPanelSize[ 0 ], _dragStartPanelSize[ 1 ] );

		// figure out the deltas of the other panels from the base panel
		for (int i=0; i<_controlGroup.Count(); ++i)
		{
			int cx, cy;
			_controlGroup[i].Get()->GetPos(cx, cy);
			_groupDeltaX.AddToTail(cx - x);
			_groupDeltaY.AddToTail(cy - y);
		}
						
		// if this panel wasn't already selected update the buildmode dialog controls to show its info
		if(_currentPanel != panel)
		{			
			_currentPanel = panel;
			
			if ( m_hBuildDialog )
			{
				// think this is taken care of by SetActiveControl.
				//ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("ApplyDataToControls"), NULL);
				
				KeyValues *keyval = new KeyValues("SetActiveControl");
				keyval->SetPtr("PanelPtr", GetCurrentPanel());
				ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), keyval, NULL);
			}		
		}		

		// store undo information upon panel selection.
		ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("StoreUndo"), NULL);

		panel->RequestFocus();
	}

	return true;
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
bool BuildGroup::MouseReleased(MouseCode code, Panel *panel)
{
	if ( !m_hBuildDialog.Get() )
	{
		if ( panel->GetParent() )
		{
			EditablePanel *ep = dynamic_cast< EditablePanel * >( panel->GetParent() );
			if ( ep )
			{
				BuildGroup *bg = ep->GetBuildGroup();
				if ( bg && bg != this )
				{
					bg->MouseReleased( code, panel );
				}
			}
		}
		return false;
	}

	Assert(panel);

	_dragging=false;
	input()->SetMouseCapture(null);
	return true;
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
bool BuildGroup::MouseDoublePressed(MouseCode code, Panel *panel)
{
	Assert(panel);
	return MousePressed( code, panel );
}

bool BuildGroup::KeyTyped( wchar_t unichar, Panel *panel )
{
	if ( !m_hBuildDialog.Get() )
	{
		if ( panel->GetParent() )
		{
			EditablePanel *ep = dynamic_cast< EditablePanel * >( panel->GetParent() );
			if ( ep )
			{
				BuildGroup *bg = ep->GetBuildGroup();
				if ( bg && bg != this )
				{
					bg->KeyTyped( unichar, panel );
				}
			}
		}
		return false;
	}

	return true;
}


//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
bool BuildGroup::KeyCodeTyped(KeyCode code, Panel *panel)
{
	if ( !m_hBuildDialog.Get() )
	{
		if ( panel->GetParent() )
		{
			EditablePanel *ep = dynamic_cast< EditablePanel * >( panel->GetParent() );
			if ( ep )
			{
				BuildGroup *bg = ep->GetBuildGroup();
				if ( bg && bg != this )
				{
					bg->KeyCodeTyped( code, panel );
				}
			}
		}
		return false;
	}

	Assert(panel);

	int dx=0;
	int dy=0;

	bool shift = ( input()->IsKeyDown(KEY_LSHIFT) || input()->IsKeyDown(KEY_RSHIFT) );
	bool ctrl = ( input()->IsKeyDown(KEY_LCONTROL) || input()->IsKeyDown(KEY_RCONTROL) );
	bool alt = (input()->IsKeyDown(KEY_LALT) || input()->IsKeyDown(KEY_RALT));

	
	if ( ctrl && shift && alt && code == KEY_B)
	{
		// enable build mode
		EditablePanel *ep = dynamic_cast< EditablePanel * >( panel );
		if ( ep )
		{
			ep->ActivateBuildMode();
		}
		return true;
	}

	switch (code)
	{
		case KEY_LEFT:
		{
			dx-=_snapX;
			break;
		}
		case KEY_RIGHT:
		{
			dx+=_snapX;
			break;
		}
		case KEY_UP:
		{
			dy-=_snapY;
			break;
		}
		case KEY_DOWN:
		{
			dy+=_snapY;
			break;
		}
		case KEY_DELETE:
		{
			// delete the panel we have selected 
			ivgui()->PostMessage (m_hBuildDialog->GetVPanel(), new KeyValues ("DeletePanel"), NULL);
			break;
		}

	}

	if (ctrl)
	{
		switch (code)
		{
		case KEY_Z:
			{
				ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("Undo"), NULL);
				break;
			}

		case KEY_C:
			{
				ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("Copy"), NULL);
				break;
			}
		case KEY_V:
			{
				ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("Paste"), NULL);
				break;
			}
		}
	}

	if(dx||dy)
	{
		//TODO: make this stuff actually snap

		int x,y,wide,tall;

		panel->GetBounds(x,y,wide,tall);

		if(shift)
		{
			panel->SetSize(wide+dx,tall+dy);
		}
		else
		{
			panel->SetPos(x+dx,y+dy);
		}

		ApplySnap(panel);

		panel->Repaint();
		if (panel->GetVParent() != 0)
		{
			panel->PostMessage(panel->GetVParent(), new KeyValues("Repaint"));
		}


		// update the build dialog
		if (m_hBuildDialog)
		{
			// post that it's active
			KeyValues *keyval = new KeyValues("SetActiveControl");
			keyval->SetPtr("PanelPtr", GetCurrentPanel());
			ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), keyval, NULL);

			// post that it's been changed
			ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), new KeyValues("PanelMoved"), NULL);
		}
	}

	// If holding key while dragging, simulate moving cursor so shift/ctrl key changes take effect
	if ( _dragging && panel != GetContextPanel() )
	{
		int x, y;
		input()->GetCursorPos( x, y );
		CursorMoved( x, y, panel );
	}

	return true;
}

bool BuildGroup::KeyCodeReleased(KeyCode code, Panel *panel )
{
	if ( !m_hBuildDialog.Get() )
	{
		if ( panel->GetParent() )
		{
			EditablePanel *ep = dynamic_cast< EditablePanel * >( panel->GetParent() );
			if ( ep )
			{
				BuildGroup *bg = ep->GetBuildGroup();
				if ( bg && bg != this )
				{
					bg->KeyCodeTyped( code, panel );
				}
			}
		}
		return false;
	}

	// If holding key while dragging, simulate moving cursor so shift/ctrl key changes take effect
	if ( _dragging && panel != GetContextPanel() )
	{
		int x, y;
		input()->GetCursorPos( x, y );
		CursorMoved( x, y, panel );
	}

	return true;
}


//-----------------------------------------------------------------------------
// Purpose: Searches for a BuildModeDialog in the hierarchy
//-----------------------------------------------------------------------------
Panel *BuildGroup::CreateBuildDialog( void )
{
	// request the panel
	Panel *buildDialog = NULL;
	KeyValues *data = new KeyValues("BuildDialog");
	data->SetPtr("BuildGroupPtr", this);
	if (m_pBuildContext->RequestInfo(data))
	{
		buildDialog = (Panel *)data->GetPtr("PanelPtr");
	}

	// initialize the build dialog if found
	if ( buildDialog )
	{
		input()->ReleaseAppModalSurface();
	}

	return buildDialog;
}

//-----------------------------------------------------------------------------
// Purpose: Activates the build mode settings dialog
//-----------------------------------------------------------------------------
void BuildGroup::ActivateBuildDialog( void )
{
	// create the build mode dialog first time through
	if (!m_hBuildDialog.Get())
	{
		m_hBuildDialog = CreateBuildDialog();

		if (!m_hBuildDialog.Get())
			return;
	}

	m_hBuildDialog->SetVisible( true );

	// send a message to set the initial dialog controls info
	_currentPanel = m_pParentPanel;
	KeyValues *keyval = new KeyValues("SetActiveControl");
	keyval->SetPtr("PanelPtr", GetCurrentPanel());
	ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), keyval, NULL);
}

//-----------------------------------------------------------------------------
// Purpose:
//-----------------------------------------------------------------------------
HCursor BuildGroup::GetCursor(Panel *panel)
{
	Assert(panel);
	
	int x,y,wide,tall;
	input()->GetCursorPos(x,y);
	panel->ScreenToLocal(x,y);
	panel->GetSize(wide,tall);

	if(x < 2)
	{
		if(y < 4)
		{
			return _cursor_sizenwse;
		}
		else
		if(y<(tall-4))
		{
			return _cursor_sizewe;
		}
		else
		{
			return _cursor_sizenesw;
		}
	}

	return _cursor_sizeall;
}

//-----------------------------------------------------------------------------
// Purpose: 
//-----------------------------------------------------------------------------
void BuildGroup::ApplySnap(Panel *panel)
{
	Assert(panel);
	
	int x,y,wide,tall;
	panel->GetBounds(x,y,wide,tall);

	x=(x/_snapX)*_snapX;
	y=(y/_snapY)*_snapY;
	panel->SetPos(x,y);
	
	int xx,yy;
	xx=x+wide;
	yy=y+tall;
	
	xx=(xx/_snapX)*_snapX;
	yy=(yy/_snapY)*_snapY;
	panel->SetSize(xx-x,yy-y);
}

//-----------------------------------------------------------------------------
// Purpose:	Return the currently selected panel
//-----------------------------------------------------------------------------
Panel *BuildGroup::GetCurrentPanel()
{
	return _currentPanel;
}

//-----------------------------------------------------------------------------
// Purpose: Add panel the list of panels that are in the build group
//-----------------------------------------------------------------------------
void BuildGroup::PanelAdded(Panel *panel)
{
	Assert(panel);

	PHandle temp;
	temp = panel;
	int c = _panelDar.Count();
	for ( int i = 0; i < c; ++i )
	{
		if ( _panelDar[ i ] == temp )
		{
			return;
		}
	}
	_panelDar.AddToTail(temp);
}

//-----------------------------------------------------------------------------
// Purpose: loads the control settings from file
//-----------------------------------------------------------------------------
void BuildGroup::LoadControlSettings(const char *controlResourceName, const char *pathID, KeyValues *pPreloadedKeyValues, KeyValues *pConditions)
{
	// make sure the file is registered
	RegisterControlSettingsFile(controlResourceName, pathID);

	// Use the keyvalues they passed in or load them.
	KeyValues *rDat = pPreloadedKeyValues;
	if ( !rDat )
	{
		// load the resource data from the file
		rDat  = new KeyValues(controlResourceName);

		// check the skins directory first, if an explicit pathID hasn't been set
		bool bSuccess = false;
		if (!pathID)
		{
			bSuccess = rDat->LoadFromFile(g_pFullFileSystem, controlResourceName, "SKIN");
		}
		if (!bSuccess)
		{
			bSuccess = rDat->LoadFromFile(g_pFullFileSystem, controlResourceName, pathID);
		}

		if ( bSuccess )
		{
			if ( IsX360() )
			{
				rDat->ProcessResolutionKeys( surface()->GetResolutionKey() );
			}
			if ( IsPC() )
			{
				ConVarRef cl_hud_minmode( "cl_hud_minmode", true );
				if ( cl_hud_minmode.IsValid() && cl_hud_minmode.GetBool() )
				{
					rDat->ProcessResolutionKeys( "_minmode" );
				}
			}

			if ( pConditions && pConditions->GetFirstSubKey() )
			{
				ProcessConditionalKeys( rDat, pConditions );			
			}
		}
	}

	// save off the resource name
	delete [] m_pResourceName;
	m_pResourceName = new char[strlen(controlResourceName) + 1];
	strcpy(m_pResourceName, controlResourceName);

	if (pathID)
	{
		delete [] m_pResourcePathID;
		m_pResourcePathID = new char[strlen(pathID) + 1];
		strcpy(m_pResourcePathID, pathID);
	}

	// delete any controls not in both files
	DeleteAllControlsCreatedByControlSettingsFile();

	// loop through the resource data sticking info into controls
	ApplySettings(rDat);

	if (m_pParentPanel)
	{
		m_pParentPanel->InvalidateLayout();
		m_pParentPanel->Repaint();
	}

	if ( rDat != pPreloadedKeyValues )
	{
		rDat->deleteThis();
	}
}

void BuildGroup::ProcessConditionalKeys( KeyValues *pData, KeyValues *pConditions )
{
	// for each condition, look for it in keys
	// if its a positive condition, promote all of its children, replacing values

	if ( pData )
	{
		KeyValues *pSubKey = pData->GetFirstSubKey();
		if ( !pSubKey )
		{
			// not a block
			return;
		}

		for ( ; pSubKey != NULL; pSubKey = pSubKey->GetNextKey() )
		{
			// recursively descend each sub block
			ProcessConditionalKeys( pSubKey, pConditions );

			KeyValues *pCondition = pConditions->GetFirstSubKey();
			for ( ; pCondition != NULL; pCondition = pCondition->GetNextKey() )
			{
				// if we match any conditions in this sub block, copy up
				KeyValues *pConditionBlock = pSubKey->FindKey( pCondition->GetName() );
				if ( pConditionBlock )
				{
					KeyValues *pOverridingKey;
					for ( pOverridingKey = pConditionBlock->GetFirstSubKey(); pOverridingKey != NULL; pOverridingKey = pOverridingKey->GetNextKey() )
					{
						KeyValues *pExistingKey = pSubKey->FindKey( pOverridingKey->GetName() );
						if ( pExistingKey )
						{
							pExistingKey->SetStringValue( pOverridingKey->GetString() );
						}
						else
						{
							KeyValues *copy = pOverridingKey->MakeCopy();
							pSubKey->AddSubKey( copy );
						}
					}				
				}
			}			
		}		
	}
}

//-----------------------------------------------------------------------------
// Purpose: registers that a control settings file may be loaded
//			use when the dialog may have multiple states and the editor will need to be able to switch between them
//-----------------------------------------------------------------------------
void BuildGroup::RegisterControlSettingsFile(const char *controlResourceName, const char *pathID)
{
	// add the file into a list for build mode
	CUtlSymbol sym(controlResourceName);
	if (!m_RegisteredControlSettingsFiles.IsValidIndex(m_RegisteredControlSettingsFiles.Find(sym)))
	{
		m_RegisteredControlSettingsFiles.AddToTail(sym);
	}
}

//-----------------------------------------------------------------------------
// Purpose: data accessor / iterator
//-----------------------------------------------------------------------------
int BuildGroup::GetRegisteredControlSettingsFileCount()
{
	return m_RegisteredControlSettingsFiles.Count();
}

//-----------------------------------------------------------------------------
// Purpose: data accessor
//-----------------------------------------------------------------------------
const char *BuildGroup::GetRegisteredControlSettingsFileByIndex(int index)
{
	return m_RegisteredControlSettingsFiles[index].String();
}

//-----------------------------------------------------------------------------
// Purpose: reloads the control settings from file
//-----------------------------------------------------------------------------
void BuildGroup::ReloadControlSettings()
{
	delete m_hBuildDialog.Get(); 
	m_hBuildDialog = NULL;

	// loop though objects in the current control group and remove them all
	// the 0th panel is always the contextPanel which is not deletable 
	for( int i = 1; i < _panelDar.Count(); i++ )
	{	
		if (!_panelDar[i].Get()) // this can happen if we had two of the same handle in the list
		{
			_panelDar.Remove(i);
			--i;
			continue;
		}
		
		// only delete deletable panels, as the only deletable panels
		// are the ones created using the resource file
		if ( _panelDar[i].Get()->IsBuildModeDeletable())
		{
			delete _panelDar[i].Get();
			_panelDar.Remove(i);
			--i;
		}		
	}	

	if (m_pResourceName)
	{
		EditablePanel *edit = dynamic_cast<EditablePanel *>(m_pParentPanel);
		if (edit)
		{
			edit->LoadControlSettings(m_pResourceName, m_pResourcePathID);
		}
		else
		{
			LoadControlSettings(m_pResourceName, m_pResourcePathID);
		}
	}

	_controlGroup.RemoveAll();	

	ActivateBuildDialog();	
}

//-----------------------------------------------------------------------------
// Purpose: changes which control settings are currently loaded
//-----------------------------------------------------------------------------
void BuildGroup::ChangeControlSettingsFile(const char *controlResourceName)
{
	// clear any current state
	_controlGroup.RemoveAll();
	_currentPanel = m_pParentPanel;

	// load the new state, via the dialog if possible
	EditablePanel *edit = dynamic_cast<EditablePanel *>(m_pParentPanel);
	if (edit)
	{
		edit->LoadControlSettings(controlResourceName, m_pResourcePathID);
	}
	else
	{
		LoadControlSettings(controlResourceName, m_pResourcePathID);
	}

	// force it to update
	KeyValues *keyval = new KeyValues("SetActiveControl");
	keyval->SetPtr("PanelPtr", GetCurrentPanel());
	ivgui()->PostMessage(m_hBuildDialog->GetVPanel(), keyval, NULL);
}

//-----------------------------------------------------------------------------
// Purpose: saves control settings to file
//-----------------------------------------------------------------------------
bool BuildGroup::SaveControlSettings( void )
{
	bool bSuccess = false;
	if ( m_pResourceName )
	{
		KeyValues *rDat = new KeyValues( m_pResourceName );

		// get the data from our controls
		GetSettings( rDat );
		
		char fullpath[ 512 ];
		g_pFullFileSystem->RelativePathToFullPath( m_pResourceName, m_pResourcePathID, fullpath, sizeof( fullpath ) );

		// save the data out to a file
		bSuccess = rDat->SaveToFile( g_pFullFileSystem, fullpath, NULL );
		if (!bSuccess)
		{
			MessageBox *dlg = new MessageBox("BuildMode - Error saving file", "Error: Could not save changes.  File is most likely read only.");
			dlg->DoModal();
		}

		rDat->deleteThis();
	}

	return bSuccess;
}

//-----------------------------------------------------------------------------
// Purpose: Deletes all the controls not created by the code
//-----------------------------------------------------------------------------
void BuildGroup::DeleteAllControlsCreatedByControlSettingsFile()
{
	// loop though objects in the current control group and remove them all
	// the 0th panel is always the contextPanel which is not deletable 
	for ( int i = 1; i < _panelDar.Count(); i++ )
	{	
		if (!_panelDar[i].Get()) // this can happen if we had two of the same handle in the list
		{
			_panelDar.Remove(i);
			--i;
			continue;
		}
		
		// only delete deletable panels, as the only deletable panels
		// are the ones created using the resource file
		if ( _panelDar[i].Get()->IsBuildModeDeletable())
		{
			delete _panelDar[i].Get();
			_panelDar.Remove(i);
			--i;
		}		
	}

	_currentPanel = m_pBuildContext;
	_currentPanel->InvalidateLayout();
    m_pBuildContext->Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: serializes settings from a resource data container
//-----------------------------------------------------------------------------
void BuildGroup::ApplySettings( KeyValues *resourceData )
{
	// loop through all the keys, applying them wherever
	for (KeyValues *controlKeys = resourceData->GetFirstSubKey(); controlKeys != NULL; controlKeys = controlKeys->GetNextKey())
	{
		bool bFound = false;

		// Skip keys that are atomic..
		if (controlKeys->GetDataType() != KeyValues::TYPE_NONE)
			continue;

		char const *keyName = controlKeys->GetName();

		// check to see if any buildgroup panels have this name
		for ( int i = 0; i < _panelDar.Count(); i++ )
		{
			Panel *panel = _panelDar[i].Get();

			if (!panel) // this can happen if we had two of the same handle in the list
			{
				_panelDar.Remove(i);
				--i;
				continue;
			}


			Assert (panel);

			// make the control name match CASE INSENSITIVE!
			char const *panelName = panel->GetName();

			if (!Q_stricmp(panelName, keyName))
			{
				// apply the settings
				panel->ApplySettings(controlKeys);
				bFound = true;
				break;
			}
		}

		if ( !bFound )
		{
			// the key was not found in the registered list, check to see if we should create it
			if ( keyName /*controlKeys->GetInt("AlwaysCreate", false)*/ )
			{
				// create the control even though it wasn't registered
				NewControl( controlKeys );
			}
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose: Create a new control in the context panel
// Input:	name: class name of control to create
//			controlKeys: keyvalues of settings for the panel.
//			name OR controlKeys should be set, not both.  
//			x,y position relative to base panel
// Output: Panel *newPanel, NULL if failed to create new control.
//-----------------------------------------------------------------------------
Panel *BuildGroup::NewControl( const char *name, int x, int y)
{
	Assert (name);
	
	Panel *newPanel = NULL;
	// returns NULL on failure
	newPanel = static_cast<EditablePanel *>(m_pParentPanel)->CreateControlByName(name);
	
	if (newPanel)
	{
		// panel successfully created
		newPanel->SetParent(m_pParentPanel);	
		newPanel->SetBuildGroup(this);
		newPanel->SetPos(x, y);

		char newFieldName[255];
		GetNewFieldName(newFieldName, sizeof(newFieldName), newPanel);
		newPanel->SetName(newFieldName);
		
		newPanel->AddActionSignalTarget(m_pParentPanel);
		newPanel->SetBuildModeEditable(true);
		newPanel->SetBuildModeDeletable(true);	
		
		// make sure it gets freed
		newPanel->SetAutoDelete(true);
	}	

	return newPanel;
}

//-----------------------------------------------------------------------------
// Purpose: Create a new control in the context panel
// Input:	controlKeys: keyvalues of settings for the panel only works when applying initial settings.
// Output:	Panel *newPanel, NULL if failed to create new control.
//-----------------------------------------------------------------------------
Panel *BuildGroup::NewControl( KeyValues *controlKeys, int x, int y)
{
	Assert (controlKeys);
	
	Panel *newPanel = NULL;
	if (controlKeys)
	{
//		Warning( "Creating new control \"%s\" of type \"%s\"\n", controlKeys->GetString( "fieldName" ), controlKeys->GetString( "ControlName" ) );
		KeyValues *keyVal = new KeyValues("ControlFactory", "ControlName", controlKeys->GetString("ControlName"));
		m_pBuildContext->RequestInfo(keyVal);
		// returns NULL on failure
		newPanel = (Panel *)keyVal->GetPtr("PanelPtr");
		keyVal->deleteThis();
	}
	else
	{
		return NULL;
	}

	if (newPanel)
	{
		// panel successfully created
		newPanel->SetParent(m_pParentPanel);	
		newPanel->SetBuildGroup(this);
		newPanel->SetPos(x, y);

		newPanel->SetName(controlKeys->GetName()); // name before applysettings :)
		newPanel->ApplySettings(controlKeys);

		newPanel->AddActionSignalTarget(m_pParentPanel);
		newPanel->SetBuildModeEditable(true);
		newPanel->SetBuildModeDeletable(true);	
		
		// make sure it gets freed
		newPanel->SetAutoDelete(true);
	}	

	return newPanel;
}

//-----------------------------------------------------------------------------
// Purpose: Get a new unique fieldname for a new control
//-----------------------------------------------------------------------------
void BuildGroup::GetNewFieldName(char *newFieldName, int newFieldNameSize, Panel *newPanel)
{
	int fieldNameNumber=1;
	char defaultName[25];
	
	Q_strncpy( defaultName, newPanel->GetClassName(), sizeof( defaultName ) );

	while (1)
	{
		Q_snprintf (newFieldName, newFieldNameSize, "%s%d", defaultName, fieldNameNumber);
		if ( FieldNameTaken(newFieldName) == NULL)
			break;
		++fieldNameNumber;
	}	
}

//-----------------------------------------------------------------------------
// Purpose: check to see if any buildgroup panels have this fieldname
// Input  : fieldName, name to check
// Output : ptr to a panel that has the name if it is taken
//-----------------------------------------------------------------------------
Panel *BuildGroup::FieldNameTaken(const char *fieldName)
{	 	
	for ( int i = 0; i < _panelDar.Count(); i++ )
	{
		Panel *panel = _panelDar[i].Get();
		if ( !panel )
			continue;

		if (!stricmp(panel->GetName(), fieldName) )
		{
			return panel;
		}
	}
	return NULL;
}

//-----------------------------------------------------------------------------
// Purpose: serializes settings to a resource data container
//-----------------------------------------------------------------------------
void BuildGroup::GetSettings( KeyValues *resourceData )
{
	// loop through all the objects getting their settings
	for( int i = 0; i < _panelDar.Count(); i++ )
	{
		Panel *panel = _panelDar[i].Get();
		if (!panel)
			continue;

		bool isRuler = false;
		// do not get setting for ruler labels.
		if (_showRulers) // rulers are visible
		{
			for (int i = 0; i < 4; i++)
			{
				if (panel == _rulerNumber[i])
				{
					isRuler = true;
					break;
				}
			}
			if (isRuler)
			{
				isRuler = false;
				continue;
			}
		}

		// Don't save the setting of the buildmodedialog
		if (!stricmp(panel->GetName(), "BuildDialog"))
			continue;

		// get the keys section from the data file
		if (panel->GetName() && *panel->GetName())
		{
			KeyValues *datKey = resourceData->FindKey(panel->GetName(), true);

			// get the settings
			panel->GetSettings(datKey);
		}
	}
}

//-----------------------------------------------------------------------------
// Purpose: loop though objects in the current control group and remove them all
//-----------------------------------------------------------------------------
void BuildGroup::RemoveSettings()
{	
	// loop though objects in the current control group and remove them all
	int i;
	for( i = 0; i < _controlGroup.Count(); i++ )
	{		
		// only delete delatable panels
		if ( _controlGroup[i].Get()->IsBuildModeDeletable())
		{
			delete _controlGroup[i].Get();
			_controlGroup.Remove(i);
			--i;
		}		
	}
	
	// remove deleted panels from the handle list
	for( i = 0; i < _panelDar.Count(); i++ )
	{
		if ( !_panelDar[i].Get() )	
		{	
		  _panelDar.Remove(i);
		  --i;
		}
	}

	_currentPanel = m_pBuildContext;
	_currentPanel->InvalidateLayout();
    m_pBuildContext->Repaint();
}

//-----------------------------------------------------------------------------
// Purpose: sets the panel from which the build group gets all it's object creation info
//-----------------------------------------------------------------------------
void BuildGroup::SetContextPanel(Panel *contextPanel)
{
	m_pBuildContext = contextPanel;
}

//-----------------------------------------------------------------------------
// Purpose: gets the panel from which the build group gets all it's object creation info
//-----------------------------------------------------------------------------
Panel *BuildGroup::GetContextPanel() 
{
	return m_pBuildContext;
}

//-----------------------------------------------------------------------------
// Purpose: get the list of panels in the buildgroup
//-----------------------------------------------------------------------------
CUtlVector<PHandle> *BuildGroup::GetPanelList() 
{
	return &_panelDar;
}

//-----------------------------------------------------------------------------
// Purpose: dialog variables
//-----------------------------------------------------------------------------
KeyValues *BuildGroup::GetDialogVariables()
{
	EditablePanel *edit = dynamic_cast<EditablePanel *>(m_pParentPanel);
	if (edit)
	{
		return edit->GetDialogVariables();
	}

	return NULL;
}