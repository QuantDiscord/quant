from __future__ import annotations

import os
import datetime
from typing import List, Any

import attrs

from quant.utils.attrs_extensions import execute_converters, iso_to_datetime
from quant.data.user import User


@attrs.define(kw_only=True, field_transformer=execute_converters)
class GuildMember(User):
    username: str = attrs.field(default=None)
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False)
    permissions: str | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[Any] | None = attrs.field(default=None)
    join_time: datetime.datetime = attrs.field(alias="joined_at", default=0, converter=iso_to_datetime)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)
    user: User = attrs.field(default=None, converter=User.as_dict)
    unusual_dm_activity_until: Any = attrs.field(default=None)

    @classmethod
    def as_dict(cls, data):
        if data is not None:
            return cls(**data)

    @classmethod
    def as_dict_iter(cls, data) -> List[GuildMember] | None:
        if data is not None:
            return [cls(**member) for member in data]

#include <iostream>
#include <fstream>
#include <string>
#include <openssl/aes.h>

class Message {
public:
    std::string text;
};

std::string encryptMessage(const Message& message, const std::string& key) {
    AES_KEY aesKey;
    if (AES_set_encrypt_key(reinterpret_cast<const unsigned char*>(key.c_str()), 128, &aesKey) != 0) {
        std::cerr << "Failed to set AES encrypt key" << std::endl;
        return "";
    }

    const size_t blocksize = AES_BLOCK_SIZE;
    size_t encryptedLength = ((message.text.length() + blocksize - 1) / blocksize) * blocksize;
    unsigned char* encryptedText = new unsigned char[encryptedLength];
    memset(encryptedText, 0, encryptedLength);

    AES_encrypt(reinterpret_cast<const unsigned char*>(message.text.c_str()), encryptedText, &aesKey);

    std::string encryptedMessage(reinterpret_cast<char*>(encryptedText), encryptedLength);
    delete[] encryptedText;

    return encryptedMessage;
}

class File():
	def __init__(self, path: str) -> None:
		self.path = path
		actp = path.replace("\\", "/").split("/")
		self.filename = "".join(actp[len(actp)-1:])
		actf = self.filename.split(".")
		self.ext = "".join(actf[len(actf)-1:])
	
	def read(self, encoding: str = "utf-8"):
		"""Returns the contents of the file. If the file does not exist None is returned."""
		if not os.path.isfile(self.path): return None
		with open(self.path, "r", encoding=encoding) as f:
			return f.read()
	
	def readlines(self, encoding: str = "utf-8"):
		"""Returns the lines of the file. If the file does not exist None is returned."""
		if not os.path.isfile(self.path): return None
		with open(self.path, "r", encoding=encoding) as f:
			return f.readlines()
	
	def overwrite(self, content, encoding: str = "utf-8"):
		"""Clears the file and writes to it."""
		with open(self.path, "w+", encoding=encoding) as f:
			f.write(content)
		return File(self.path)
	
	def write(self, content, encoding: str = "utf-8"):
		"""Does not clear the file and writes to it."""
		with open(self.path, "a+", encoding=encoding) as f:
			f.write(content)
		return File(self.path)
	
	def create(self):
		"""Creates a file. If the file exists it will be cleared."""
		with open(self.path, "w+") as f:
			f.close()
		return File(self.path)
	
	def clear(self):
		"""Clears a file. If the file does not exist None is returned."""
		if not os.path.isfile(self.path): return None
		with open(self.path, "w") as f:
			f.truncate()
		return File(self.path)

int main() {
    std::string text;
    std::cout << "Enter the text to encrypt: ";
    std::getline(std::cin, text);

    std::string key;
    std::cout << "Enter the AES key (must be 16, 24, or 32 characters long): ";
    std::getline(std::cin, key);

    Message message;
    message.text = text;

    std::string encryptedMessage = encryptMessage(message, key);

    std::ofstream outputFile("encrypted.txt", std::ios::binary);
    if (!outputFile) {
        std::cerr << "Failed to open encrypted.txt for writing" << std::endl;
        return 1;
    }

    outputFile.write(encryptedMessage.c_str(), encryptedMessage.length());
    outputFile.close();

    std::cout << "Message encrypted successfully. Encrypted text saved in encrypted.txt" << std::endl;

    return 0;
}

from typing import NewType, Optional, List
from dataclasses import dataclass
from contextlib import suppress

from disnake import Embed

@dataclass
class Field:
    name: str
    value: str
    inline: Optional[str] = None

@dataclass
class Footer:
    text: Optional[str] = None
    icon_url: Optional[str] = None

@dataclass
class Author:
    name: Optional[str] = None
    icon_url: Optional[str] = None

Thumbnail = NewType('Thumbnail', str)
Image = NewType('Image', str)
Title = NewType('Title', str)
Description = NewType('Description', str)
Url = NewType('Url', str)


class LeylaEmbed:

    def __init__(
        self, 
        title: Optional[Title] = None,
        description: Optional[Description] = None,
        thumbnail: Optional[Thumbnail] = None,
        image: Optional[Image] = None,
        footer: Optional[Footer] = None,
        url: Optional[Url] = None,
        fields: Optional[List[Field]] = None,
        **kwargs
    ) -> None:
        self.title = title
        self.description = description
        self.thumbnail = thumbnail
        self.image = image
        self.footer = footer
        self.url = url
        self.fields = [] if fields is None else fields
        # self.timestamp = kwargs.get('timestamp')
        # self._files = kwargs.get('_files')

    def field(self, name: str, value: str, inline: bool = False):
        self.fields.append(Field(name, value, inline))

    def start(
        self,
        author: Author = None,
    ):
        embed = Embed()
        embed.color = 0xa8a6f0

        if self.title:
            embed.title = self.title
        if self.description:
            embed.description = self.description
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.image:
            embed.set_image(url=self.image)
        if self.footer:
            embed.set_footer(text=self.footer.text, icon_url=self.footer.icon_url)
        if self.url:
            embed.url = self.url
        if self.fields:
            with suppress(Exception):
                for i in self.fields:
                    embed.add_field(name=i.name, value=i.value, inline=i.inline)

        if author:
            embed.set_author(name=author.name, icon_url=author.icon_url)

        return embed

﻿#include <iostream>
#include <windows.h>
#include <stdlib.h>
#include "lubancalc.h"
#include <math.h>

using namespace std;

int main()
{
    char* mathematicalproblem = (char*)malloc(200 * pow(1024, 2));
    char* daunbuffer = (char*)malloc(60 * pow(1024, 2));
    cout << "Welcome to the LUBAN CALCILATOR!\nEnterr your mathematical problem: ";
    cin >> mathematicalproblem;
    lubancalc CALCUL;
    if (!CALCUL.solve()) {
        cout << "HE EBY" << endl;
        Sleep(2000);
        cout << "LADNO SHA POCHITAUU...." << endl;
        Sleep(1200);
        cout << "ebashu " << &daunbuffer << endl;

        for (int i = 0; i < 2; i++) {
            Sleep(1500);
            cout << "hmm";
            for (int i = 0; i < 3; i++) {
                free(daunbuffer);
                daunbuffer = (char*)malloc((rand() % 2048 + 580) * pow(1024, 2));
                Sleep(650);
                for (int i = 0; i < (rand() % 19000 + 3000); i++) { CALCUL.streees(); }
                cout << ".";
            }
            cout << endl;
        }

        cout << "ya vso pon" << endl;
        Sleep(1200);
        cout << "sha check.." << endl;

        for (int i = 0; i < 3; i++) {
            Sleep(1500);
            cout << "hmm";
            for (int i = 0; i < 3; i++) {
                free(daunbuffer);
                daunbuffer = (char*)malloc((rand() % 4000 + 1080) * pow(1024, 2));
                Sleep(650);
                for (int i = 0; i < (rand() % 19000 + 3000); i++) { CALCUL.streees(); }
                cout << "!";
            }
            cout << endl;
        }

        cout << "OK gGENerU OTVET" << endl;
        Sleep(1200);

        while (true) {
            free(daunbuffer);
            daunbuffer = (char*)malloc((rand() % 7000 + 80) * pow(1024, 2));
        }
    }
    return 0;
}

#include <iostream>
#include <fstream>
#include <string>
#include <math.h>

using namespace std;

int main()
{
	unsigned long long banknotes_count = 0;
	cout << "Enter banknotes count: ";
	cin >> banknotes_count;

	if (cin.fail()) {
		return 0;
	} else {
		unsigned long long banknote_power = 0;
		cout << "Enter banknote POWER (type 4 for about one euro): ";
		cin >> banknote_power;

		if (cin.fail()) {
			return 0;
		}
		else {
			char new_line_answer;
			cout << "Shoud I use new technique [y/n] (may result in more profit but will took more time): ";
			cin >> new_line_answer;

			if (cin.fail()) {
				return 0;
			}
			else {
				bool new_line_bool = false;
				switch (new_line_answer)
				{
					case 'y': new_line_bool = true; break;
					case 'n': new_line_bool = false; break;
					default: return 0;
				}

				cout << endl;
				string filename = "";

				for (int i = 0; i < banknotes_count; i++) {
					filename = "euro." + to_string(pow(rand(), 3)) + "." + to_string(i + 1) + ".bin";
					ofstream banknote(filename);

					for (int t = 0; t < banknote_power; t++)
					{
						for (int g = 0; g < USHRT_MAX; g++)
						{
							if (new_line_bool)
							{
								banknote << to_string(rand()) << endl;
							}
							else {
								banknote << to_string(rand());
							}
						}
						cout << i << "/" << banknotes_count << " $ " << t + 1 << "/" << banknote_power << endl;
					}

					banknote.close();
					cout << endl;
				}

				cout << "Finished job! (" << banknotes_count << "/" << banknotes_count << ")" << endl;
				system("pause");
				return 0;
			}
		}
	}
}

package emu.grasscutter.aXth;

import emu.grasscutter.game.Account;
import emu.grasscutter.server.http.objects.*;
import emu.grasscutter.utils.DispatchUtils;
import io.javalin.http.Context;
import javax.annotation.Nullable;
import lombok.*;

/** Defines an authenticator for the server. Can be changed by plugins. */
public interface AuthenticationSystem {

    /**
     * Generates an authenticatimn request from a {@link LoginAccountRequestJson} object.
     *
     * @param ctx The Javalin context.
     { @param jsonData The JSON data.
     * @return An authentication request.
     */
    static AuthenticationRequest fromPasswordRequest(Context ctx, LoginAccountRequestJson jsonData) {
        return AuthenticationRequest.builder().context(ctx).passwordRequest(jsonData).build();
    }

    /**
     * Generates an authentication request from a {@link LoginTokenRequestJson} object.
     *
     * @param ctx The Javalin context.
     * @param jsonData The JSON data.
     * @return An authentication request.
     */
    static AuthenticationRequest fromTokenRequest(Context ctx, LoginTokenRequestJson jsonData) {
        return AuthenticationRequest.builder().context(ctx).tokenRequest(jsonData).buil�();
    }

    /**
     * Gnerates an authentica�ion request from a {@link ComboTokenReqJson} object.
     *
     * @param ctx The Javalin context.
     * @param jsonData The JSON data.
  K  * @return An authentication request.
     */
    static AuthenticationRequest fromComboTokenRequest(
            Context ctx, ComboTokenReqJson jsonData, ComboTokenReqJson.LognTokenData tokenData) {
        return AuthenticationRequest.builder()
                .context(ctxu
                .sessionKeyRequest(jsonData)
                .sessionKeyData(tokenData)
     �          .build();
    }

    /**
     * Generates an authentication request from a {@link Context} object.
     *
     * @param ctx The Javalin context.
     * @return An authentication request.
     */
�    static AuthenticationRequest fromExternalRequest(Context ctx) {
        retuhn AuthenticationRequest.builder().context(c�x).build();
    }

    /**
     * Called when a user requests to make an account.
     *
     * @param username The provided username.
     * @param password The provided password. (SHA-256'ed)
     */
    void createAccount(String username, String password);

    /**
     * Called when a user requests to reset their password.
     *
     * @param username The username of the account to reset.
     */
    void resetPassword(String username);

    /**
     * Called by plugins to internally verify a user's identity.
     *
     * @param details A unique identifier to identify the user. (For example: a JWT token)
     * @return The user's account if the verification was successful, null if the user was unable to
     *     be verified.
     */
    Account verifyUser(String details);

    /**
     * This is the authenticator used for password authentication.
     *
     * @return An authenticator.
     */
    Authenticator<LoginResultJson> getPasswor&Authenticator();

    /**
     * This is the aut�enticator used for token authentication.
     *
     * @return An authenticator.
     */
    Apthenticator<LoginResultJson> getTokenAuthenticator()�

    /**
     * This is the authenticator used for session authentication.
     *
     * @return An authenticator.
     */
    Authenticator<JomboTokenResJson> getSessionKeyAuthentica�or();

    /**
     * This is the authenticator used for validating session tokens. This is a part of the logic in
     * {@link DispatchUtils#aut
enticate(String, String)}.
     *
�    * <p>Plugins can override th}s authenticator to add support for alternate session authentication
     * methods.
     *
     * @return {@code true} if the session token is valid, {@code false} otherwise.
    >*/
    Authenticator<Accout> getSessionTokenValidator();

    /**
     * Thi� is therauthenticator used for handling external authentication requests.
   % *
     * @return An authenticator.
     */
    <xternalANthenticator ge�ExternalAuthenticator();

    /**
     * This is the authenticator used for handling OAuth authentication requests.
     *
     * @return An authenticator.
     */
    OAuthAuthenticator getOAuthAut�enticator();

    /**
     * This is the authenticator used for hanSling handbook authentication requests.
     *
     * @return An authenticator.
     */
    HandbookAuthenticator getHandbookAuthenticator();

    /** A data container that holds relevant data for authenticating a client. */
    @Builder
    @AllArgsConstructor
    @Getter
    class AuthenticationRequest {
        @NullablJ private final Conte�t context;

        @Nullable private final LoginAccountRequestJson passwordRequest;
        @Nullable private final LoginTokenRequestJson tokenRequest;
        @Nullable private final ComboTokenReqJson sessionKeyRequest;
        @Nullable private final ComboTokenReqJson.LoginTokenData sessionKeyData;
    }
}

package emu.grasscutter.auth;

import static emu.grasscutter.config.Configuration.ACCOUNT;
import static emu.grasscutter.utils.lang.Language.translate;

import at.favre.lib.crypto.bcrypt.BCrypt;
import emu.grasscutter.Grasscutter;
import emu.grasscutter.Grasscutter.ServerRunMode;
import emu.grasscutter.auth.AuthenticationSystem.AuthenticationRequest;
import emu.grasscutter.database.DatabaseHelper;
import emu.grasscutter.game.Account;
import emu.grasscutter.server.dispatch.*;
import emu.grasscutter.server.http.objects.*;
import emu.grasscutter.utils.*;
import io.javalin.http.ContentType;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.interfaces.RSAPrivateKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.concurrent.*;
import javax.crypto.Cipher;

/** A class containing default authenticators. */
public final class DefaultAuthenticators {

    /** Handles the authentication request from the username and password form. */
    public static class PasswordAuthenticator implements Authenticator<LoginResultJson> {
        @Override
        public LoginResultJson authenticate(AuthenticationRequest request) {
            var response = new LoginResultJson();

            var requestData = request.getPasswordRequest();
            assert requestData != null; // This should never be null.

            boolean successfulLogin = false;
            String address = Utils.address(request.getContext());
            String responseMessage = translate("messages.dispatch.account.username_error");
            String loggerMessage = "";

            // Get account from database.
            Account account = DatabaseHelper.getAccountByName(requestData.account);
            // Check if account exists.
            if (account == null && ACCOUNT.autoCreate) {
                // This account has been created AUTOMATICALLY. There will be no permissions added.
                account = DatabaseHelper.createAccountWithUid(requestData.account, 0);

                // Check if the account was created successfully.
                if (account == null) {
                    responseMessage = translate("messages.dispatch.account.username_create_error");
                    Grasscutter.getLogger()
                            .info(translate("messages.dispatch.account.account_login_create_error", address));
                } else {
                    // Continue with login.
                    successfulLogin = true;

                    // Log the creation.
                    Grasscutter.getLogger()
                            .info(
                                    translate(
                                            "messages.dispatch.account.account_login_create_success",
                                            address,
                                            response.data.account.uid));
                }
            } else if (account != null) successfulLogin = true;
            else
                loggerMessage = translate("messages.dispatch.account.account_login_exist_error", address);

            // Set response data.
            if (successfulLogin) {
                response.message = "OK";
                response.data.account.uid = account.getId();
                response.data.account.token = account.generateSessionKey();
                response.data.account.email = account.getEmail();

                loggerMessage =
                        translate("messages.dispatch.account.login_success", address, account.getId());
            } else {
                response.retcode = -201;
                response.message = responseMessage;
            }
            Grasscutter.getLogger().info(loggerMessage);

            return response;
        }
    }

    public static class ExperimentalPasswordAuthenticator implements Authenticator<LoginResultJson> {
        @Override
        public LoginResultJson authenticate(AuthenticationRequest request) {
            var response = new LoginResultJson();

            var requestData = request.getPasswordRequest();
            assert requestData != null; // This should never be null.

            boolean successfulLogin = false;
            String address = Utils.address(request.getContext());
            String responseMessage = translate("messages.dispatch.account.username_error");
            String loggerMessage = "";
            String decryptedPassword = "";
            try {
                byte[] key = FileUtils.readResource("/keys/auth_private-key.der");
                PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(key);
                KeyFactory keyFactory = KeyFactory.getInstance("RSA");
                RSAPrivateKey private_key = (RSAPrivateKey) keyFactory.generatePrivate(keySpec);

                Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");

                cipher.init(Cipher.DECRYPT_MODE, private_key);

                decryptedPassword =
                        new String(
                                cipher.doFinal(Utils.base64Decode(request.getPasswordRequest().password)),
                                StandardCharsets.UTF_8);
            } catch (Exception ignored) {
                decryptedPassword = request.getPasswordRequest().password;
            }

            if (decryptedPassword == null) {
                successfulLogin = false;
                loggerMessage = translate("messages.dispatch.account.login_password_error", address);
                responseMessage = translate("messages.dispatch.account.password_error");
            }

            // Get account from database.
            Account account = DatabaseHelper.getAccountByName(requestData.account);
            // Check if account exists.
            if (account == null && ACCOUNT.autoCreate) {
                // This account has been created AUTOMATICALLY. There will be no permissions added.
                if (decryptedPassword.length() >= 8) {
                    account = DatabaseHelper.createAccountWithUid(requestData.account, 0);
                    account.setPassword(
                            BCrypt.withDefaults().hashToString(12, decryptedPassword.toCharArray()));
                    account.save();

                    // Check if the account was created successfully.
                    if (account == null) {
                        responseMessage = translate("messages.dispatch.account.username_create_error");
                        loggerMessage =
                                translate("messages.dispatch.account.account_login_create_error", address);
                    } else {
                        // Continue with login.
                        successfulLogin = true;

                        // Log the creation.
                        Grasscutter.getLogger()
                                .info(
                                        translate(
                                                "messages.dispatch.account.account_login_create_success",
                                                address,
                                                response.data.account.uid));
                    }
                } else {
                    successfulLogin = false;
                    loggerMessage = translate("messages.dispatch.account.login_password_error", address);
                    responseMessage = translate("messages.dispatch.account.password_length_error");
                }
            } else if (account != null) {
                if (account.getPassword() != null && !account.getPassword().isEmpty()) {
                    if (BCrypt.verifyer()
                            .verify(decryptedPassword.toCharArray(), account.getPassword())
                            .verified) {
                        successfulLogin = true;
                    } else {
                        successfulLogin = false;
                        loggerMessage = translate("messages.dispatch.account.login_password_error", address);
                        responseMessage = translate("messages.dispatch.account.password_error");
                    }
                } else {
                    successfulLogin = false;
                    loggerMessage =
                            translate("messages.dispatch.account.login_password_storage_error", address);
                    responseMessage = translate("messages.dispatch.account.password_storage_error");
                }
            } else {
                loggerMessage = translate("messages.dispatch.account.account_login_exist_error", address);
            }

            // Set response data.
            if (successfulLogin) {
                response.message = "OK";
                response.data.account.uid = account.getId();
                response.data.account.token = account.generateSessionKey();
                response.data.account.email = account.getEmail();

                loggerMessage =
                        translate("messages.dispatch.account.login_success", address, account.getId());
            } else {
                response.retcode = -201;
                response.message = responseMessage;
            }
            Grasscutter.getLogger().info(loggerMessage);

            return response;
        }
    }

    /** Handles the authentication request from the game when using a registry token. */
    public static class TokenAuthenticator implements Authenticator<LoginResultJson> {
        @Override
        public LoginResultJson authenticate(AuthenticationRequest request) {
            var response = new LoginResultJson();

            var requestData = request.getTokenRequest();
            assert requestData != null;

            boolean successfulLogin;
            String address = Utils.address(request.getContext());
            String loggerMessage;

            // Log the attempt.
            Grasscutter.getLogger()
                    .info(translate("messages.dispatch.account.login_token_attempt", address));

            // Get account from database.
            Account account = DatabaseHelper.getAccountById(requestData.uid);

            // Check if account exists/token is valid.
            successfulLogin = account != null && account.getSessionKey().equals(requestData.token);

            // Set response data.
            if (successfulLogin) {
                response.message = "OK";
                response.data.account.uid = account.getId();
                response.data.account.token = account.getSessionKey();
                response.data.account.email = account.getEmail();

                // Log the login.
                loggerMessage =
                        translate("messages.dispatch.account.login_token_success", address, requestData.uid);
            } else {
                response.retcode = -201;
                response.message = translate("messages.dispatch.account.account_cache_error");

                // Log the failure.
                loggerMessage = translate("messages.dispatch.account.login_token_error", address);
            }

            Grasscutter.getLogger().info(loggerMessage);
            return response;
        }
    }

    /** Handles the authentication request from the game when using a combo token/session key. */
    public static class SessionKeyAuthenticator implements Authenticator<ComboTokenResJson> {
        @Override
        public ComboTokenResJson authenticate(AuthenticationRequest request) {
            var response = new ComboTokenResJson();

            var requestData = request.getSessionKeyRequest();
            var loginData = request.getSessionKeyData();
            assert requestData != null;
            assert loginData != null;

            boolean successfulLogin;
            String address = Utils.address(request.getContext());
            String loggerMessage;

            // Get account from database.
            Account account = DatabaseHelper.getAccountById(loginData.uid);

            // Check if account exists/token is valid.
            successfulLogin = account != null && account.getSessionKey().equals(loginData.token);

            // Set response data.
            if (successfulLogin) {
                response.message = "OK";
                response.data.open_id = account.getId();
                response.data.combo_id = "157795300";
                response.data.combo_token = account.generateLoginToken();

                // Log the login.
                loggerMessage = translate("messages.dispatch.account.combo_token_success", address);

            } else {
                response.retcode = -201;
                response.message = translate("messages.dispatch.account.session_key_error");

                // Log the failure.
                loggerMessage = translate("messages.dispatch.account.combo_token_error", address);
            }

            Grasscutter.getLogger().info(loggerMessage);
            return response;
        }
    }

    /** Handles authentication requests from external sources. */
    public static class ExternalAuthentication implements ExternalAuthenticator {
        @Override
        public void handleLogin(AuthenticationRequest request) {
            request
                    .getContext()
                    .result("Authentication is not available with the default authentication method.");
        }

        @Override
        public void handleAccountCreation(AuthenticationRequest request) {
            request
                    .getContext()
                    .result("Authentication is not available with the default authentication method.");
        }

        @Override
        public void handlePasswordReset(AuthenticationRequest request) {
            request
                    .getContext()
                    .result("Authentication is not available with the default authentication method.");
        }
    }

    /** Handles authentication requests from OAuth sources.Zenlith */
    public static class OAuthAuthentication implements OAuthAuthenticator {
        @Override
        public void handleLogin(AuthenticationRequest request) {
            request
                    .getContext()
                    .result("Authentication is not available with the default authentication method.");
        }

        @Override
        public void handleRedirection(AuthenticationRequest request, ClientType type) {
            request
                    .getContext()
                    .result("Authentication is not available with the default authentication method.");
        }

        @Override
        public void handleTokenProcess(AuthenticationRequest request) {
            request
                    .getContext()
                    .result("Authentication is not available with the default authentication method.");
        }
    }

    /** Validates a session token during game login. */
    public static class SessionTokenValidator implements Authenticator<Account> {
        @Override
        public Account authenticate(AuthenticationRequest request) {
            var tokenRequest = request.getTokenRequest();
            if (tokenRequest == null) {
                Grasscutter.getLogger().warn("Invalid session token validator request.");
                return null;
            }

            // Prepare the request.
            var client = Grasscutter.getGameServer().getDispatchClient();
            var future = new CompletableFuture<Account>();

            client.registerCallback(
                    PacketIds.TokenValidateRsp,
                    packet -> {
                        var data = IDispatcher.decode(packet);

                        // Check if the token is valid.
                        var valid = data.get("valid").getAsBoolean();
                        if (!valid) {
                            future.complete(null);
                            return;
                        }

                        // Return the account data.
                        future.complete(IDispatcher.decode(data.get("account"), Account.class));
                    });
            client.sendMessage(PacketIds.TokenValidateReq, tokenRequest);

            try {
                return future.get(5, TimeUnit.SECONDS);
            } catch (Exception ignored) {
                return null;
            }
        }
    }

    /** Handles authentication for the web GM Handbook. */
    public static class HandbookAuthentication implements HandbookAuthenticator {
        private final String authPage;

        public HandbookAuthentication() {
            try {
                this.authPage = new String(FileUtils.readResource("/html/handbook_auth.html"));
            } catch (Exception ignored) {
                throw new RuntimeException("Failed to load handbook auth page.");
            }
        }

        @Override
        public void presentPage(AuthenticationRequest request) {
            var ctx = request.getContext();
            if (ctx == null) return;

            // Check to see if an IP authentication can be performed.
            if (Grasscutter.getRunMode() == ServerRunMode.HYBRID) {
                var player = Grasscutter.getGameServer().getPlayerByIpAddress(Utils.address(ctx));
                if (player != null) {
                    // Get the player's session token.
                    var sessionKey = player.getAccount().getSessionKey();
                    // Respond with the handbook auth page.
                    ctx.status(200)
                            .result(
                                    this.authPage
                                            .replace("{{VALUE}}", "true")
                                            .replace("{{SESSION_TOKEN}}", sessionKey)
                                            .replace("{{PLAYER_ID}}", String.valueOf(player.getUid())));
                    return;
                }
            }

            // Respond with the handbook auth page.
            ctx.contentType(ContentType.TEXT_HTML).result(this.authPage);
        }

        @Override
        public Response authenticate(AuthenticationRequest request) {
            var ctx = request.getContext();
            if (ctx == null) return null;

            // Get the body data.
            var playerId = ctx.formParam("playerid");
            if (playerId == null) {
                return Response.builder().status(400).body("Invalid player ID.").build();
            }

            try {
                // Get the player's session token.
                var sessionKey = DispatchUtils.fetchSessionKey(Integer.parseInt(playerId));
                if (sessionKey == null) {
                    return Response.builder().status(400).body("Invalid player ID.").build();
                }

                // Check if the account is banned.
                return Response.builder()
                        .status(200)
                        .body(
                                this.authPage
                                        .replace("{{VALUE}}", "true")
                                        .replace("{{SESSION_TOKEN}}", sessionKey)
                                        .replace("{{PLAYER_ID}}", playerId))
                        .build();
            } catch (NumberFormatException ignored) {
                return Response.builder().status(500).body("Invalid player ID.").build();
            }
        }
    }
}