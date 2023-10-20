from __future__ import annotations

import datetime
import asyncio
from typing import List, Any

import attrs

from quant.data.guild.messages.emoji import Emoji
from quant.data.guild.members.member import GuildMember, User
from quant.data.guild.messages.interactions.interaction import Interaction
# from quant.data.components.action_row import ActionRow
from quant.data.model import BaseModel
from quant.data.guild.messages.embeds import Embed
from quant.utils.attrs_extensions import execute_converters, int_converter, iso_to_datetime
from quant.data.gateway.snowflake import Snowflake


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Message(BaseModel):
    type: int = attrs.field(default=None)
    timestamp: datetime.datetime = attrs.field(default=None, converter=iso_to_datetime)
    channel_id: Snowflake | None = attrs.field(default=None, converter=int_converter)
    position: Snowflake | None = attrs.field(default=None)
    message_id: int | None = attrs.field(alias="id", default=None, converter=int_converter)
    guild_id: Snowflake | None = attrs.field(default=None, converter=int_converter)
    author_as_member: GuildMember | None = attrs.field(alias="member", default=None, converter=GuildMember.as_dict)
    author_as_user: User | None = attrs.field(alias="author", default=None, converter=User.as_dict)
    content: str | None = attrs.field(default=None)
    nonce: str | int | None = attrs.field(default=None)
    tts: bool | None = attrs.field(default=None)
    embeds: List[Embed] | None = attrs.field(default=None)
    edited_timestamp: str = attrs.field(default=None)
    mention_everyone: bool | None = attrs.field(default=None)
    mentions: List[User] | None = attrs.field(default=None, converter=User.as_dict_iter)
    mention_roles: List[Any] | None = attrs.field(default=None)
    mention_channels: List[Any] | None = attrs.field(default=None)
    message_reference: Any | None = attrs.field(default=None)
    components: List[Any] | None = attrs.field(default=None)
    stickers: List[Any] | None = attrs.field(default=None)
    attachments: List[Any] | None = attrs.field(default=None)
    flags: int | None = attrs.field(default=None, converter=int_converter)
    referenced_message: Message | None = attrs.field(default=None)
    pinned: bool = attrs.field(default=False)
    webhook_id: Snowflake | None = attrs.field(default=None)
    activity: Any | None = attrs.field(default=None)
    application: Any | None = attrs.field(default=None)
    application_id: Snowflake | None = attrs.field(default=None)
    interaction: Interaction | None = attrs.field(default=None, converter=Interaction.as_dict)
    thread: Any | None = attrs.field(default=None)
    sticker_items: List[Any] | None = attrs.field(default=None)
    role_subscription_data: Any | None = attrs.field(default=None)
    resolved: bool | None = attrs.field(default=None)

    async def delete(self, *, reason: str = None, delete_after: int = 0) -> None:
        await asyncio.sleep(delete_after)
        await self.client.rest.delete_message(self.channel_id, self.message_id, reason)

    async def create_reaction(self, emoji: Emoji) -> None:
        await self.client.rest.create_reaction(emoji, self.guild_id, self.channel_id, self.message_id)

package emu.grasscutter.game.ability;

import com.google.protobuf.*;
import emu.grasscutter.*;
import emu.grasscutter.data.GameData;
import emu.grasscutter.data.binout.*;
import emu.grasscutter.data.binout.AbilityModifier.AbilityModifierAction;
import emu.grasscutter.game.ability.actions.*;
import emu.grasscutter.game.ability.mixins.*;
import emu.grasscutter.game.entity.GameEntity;
import emu.grasscutter.game.player.*;
import emu.grasscutter.game.props.FightProperty;
import emu.grasscutter.net.proto.AbilityInvokeEntryOuterClass.AbilityInvokeEntry;
import emu.grasscutter.net.proto.AbilityMetaAddAbilityOuterClass.AbilityMetaAddAbility;
import emu.grasscutter.net.proto.AbilityMetaModifierChangeOuterClass.AbilityMetaModifierChange;
import emu.grasscutter.net.proto.AbilityMetaReInitOverrideMapOuterClass.AbilityMetaReInitOverrideMap;
import emu.grasscutter.net.proto.AbilityMetaSetKilledStateOuterClass.AbilityMetaSetKilledState;
import emu.grasscutter.net.proto.AbilityScalarTypeOuterClass.AbilityScalarType;
import emu.grasscutter.net.proto.AbilityScalarValueEntryOuterClass.AbilityScalarValueEntry;
import emu.grasscutter.net.proto.ModifierActionOuterClass.ModifierAction;
import emu.grasscutter.server.event.player.PlayerUseSkillEvent;
import io.netty.util.concurrent.FastThreadLocalThread;
import java.util.HashMap;
import java.util.concurrent.*;
import lombok.Getter;

public final class AbilityManager extends BasePlayerManager {
    private static final HashMap<AbilityModifierAction.Type, AbilityActionHandler> actionHandlers =
            new HashMap<>();
    private static final HashMap<AbilityMixinData.Type, AbilityMixinHandler> mixinHandlers =
            new HashMap<>();

    public static final ExecutorService eventExecutor;

    static {
        eventExecutor =
                new ThreadPoolExecutor(
                        4,
                        4,
                        60,
                        TimeUnit.SECONDS,
                        new LinkedBlockingDeque<>(1000),
                        FastThreadLocalThread::new,
                        new ThreadPoolExecutor.AbortPolicy());

        registerHandlers();
    }

    @Getter private boolean abilityInvulnerable = false;

    public AbilityManager(Player player) {
        super(player);
    }

    public static void registerHandlers() {
        var handlerClassesAction = Grasscutter.reflector.getSubTypesOf(AbilityActionHandler.class);

        for (var obj : handlerClassesAction) {
            try {
                if (obj.isAnnotationPresent(AbilityAction.class)) {
                    AbilityModifierAction.Type abilityAction = obj.getAnnotation(AbilityAction.class).value();
                    actionHandlers.put(abilityAction, obj.getDeclaredConstructor().newInstance());
                } else {
                    return;
                }
            } catch (Exception e) {
                Grasscutter.getLogger().error("Unable to register handler.", e);
            }
        }

        var handlerClassesMixin = Grasscutter.reflector.getSubTypesOf(AbilityMixinHandler.class);
        for (var obj : handlerClassesMixin) {
            try {
                if (obj.isAnnotationPresent(AbilityAction.class)) {
                    AbilityMixinData.Type abilityMixin = obj.getAnnotation(AbilityMixin.class).value();
                    mixinHandlers.put(abilityMixin, obj.getDeclaredConstructor().newInstance());
                } else {
                    return;
                }
            } catch (Exception e) {
                Grasscutter.getLogger().error("Unable to register handler.", e);
            }
        }
    }

    public void executeAction(
            Ability ability, AbilityModifierAction action, ByteString abilityData, GameEntity target) {
        var handler = actionHandlers.get(action.type);
        if (handler == null || ability == null) {
            if (DebugConstants.LOG_MISSING_ABILITY_HANDLERS) {
                Grasscutter.getLogger()
                        .debug("Missing ability action handler for {} (invoker: {}).", action.type, ability);
            }

            return;
        }

        eventExecutor.submit(
                () -> {
                    if (!handler.execute(ability, action, abilityData, target)) {
                        Grasscutter.getLogger()
                                .debug("Ability execute action failed for {} at {}.", action.type, ability);
                    }
                });
    }

    public void executeMixin(Ability ability, AbilityMixinData mixinData, ByteString abilityData) {
        var handler = mixinHandlers.get(mixinData.type);
        if (handler == null || ability == null) {
            Grasscutter.getLogger()
                    .trace("Could not execute ability mixin {} at {}", mixinData.type, ability);
            return;
        }

        eventExecutor.submit(
                () -> {
                    if (!handler.execute(ability, mixinData, abilityData)) {
                        Grasscutter.getLogger()
                                .error("Ability execute action failed for {} at {}.", mixinData.type, ability);
                    }
                });
    }

    public void onAbilityInvoke(AbilityInvokeEntry invoke) throws Exception {
        Grasscutter.getLogger()
                .trace(
                        "Ability invoke: "
                                + invoke
                                + " "
                                + invoke.getArgumentType()
                                + " ("
                                + invoke.getArgumentTypeValue()
                                + "): "
                                + this.player.getScene().getEntityById(invoke.getEntityId()));
        var entity = this.player.getScene().getEntityById(invoke.getEntityId());
        if (entity != null) {
            Grasscutter.getLogger()
                    .trace(
                            "Entity {} has a group of {} and a config of {}.",
                            invoke.getEntityId(),
                            entity.getGroupId(),
                            entity.getConfigId());

            Grasscutter.getLogger()
                    .trace(
                            "Invoke type of {} ({}) has entity {}.",
                            invoke.getArgumentType(),
                            invoke.getArgumentTypeValue(),
                            entity.getId());
        } else if (DebugConstants.LOG_ABILITIES) {
            Grasscutter.getLogger()
                    .debug(
                            "Invoke type of {} ({}) has no entity. (referring to {})",
                            invoke.getArgumentType(),
                            invoke.getArgumentTypeValue(),
                            invoke.getEntityId());
        }

        if (invoke.getHead().getTargetId() != 0) {
            Grasscutter.getLogger()
                    .trace("Target: " + this.player.getScene().getEntityById(invoke.getHead().getTargetId()));
        }
        if (invoke.getHead().getLocalId() != 0) {
            this.handleServerInvoke(invoke);
            return;
        }

        switch (invoke.getArgumentType()) {
            case ABILITY_INVOKE_ARGUMENT_META_OVERRIDE_PARAM -> this.handleOverrideParam(invoke);
            case ABILITY_INVOKE_ARGUMENT_META_REINIT_OVERRIDEMAP -> this.handleReinitOverrideMap(invoke);
            case ABILITY_INVOKE_ARGUMENT_META_MODIFIER_CHANGE -> this.handleModifierChange(invoke);
            case ABILITY_INVOKE_ARGUMENT_MIXIN_COST_STAMINA -> this.handleMixinCostStamina(invoke);
            case ABILITY_INVOKE_ARGUMENT_ACTION_GENERATE_ELEM_BALL -> this.handleGenerateElemBall(invoke);
            case ABILITY_INVOKE_ARGUMENT_META_GLOBAL_FLOAT_VALUE -> this.handleGlobalFloatValue(invoke);
            case ABILITY_INVOKE_ARGUMENT_META_MODIFIER_DURABILITY_CHANGE -> this
                    .handleModifierDurabilityChange(invoke);
            case ABILITY_INVOKE_ARGUMENT_META_ADD_NEW_ABILITY -> this.handleAddNewAbility(invoke);
            case ABILITY_INVOKE_ARGUMENT_META_SET_KILLED_SETATE -> this.handleKillState(invoke);
            default -> {
                if (DebugConstants.LOG_MISSING_ABILITIES) {
                    Grasscutter.getLogger()
                            .trace("Missing invoke handler for ability {}.", invoke.getArgumentType().name());
                }
            }
        }
    }

    public void handleServerInvoke(AbilityInvokeEntry invoke) {
        var head = invoke.getHead();

        var entity = this.player.getScene().getEntityById(invoke.getEntityId());
        if (entity == null) {
            Grasscutter.getLogger().trace("Entity not found: {}", invoke.getEntityId());
            return;
        }

        var target = this.player.getScene().getEntityById(head.getTargetId());
        if (target == null) target = entity;

        Ability ability = null;

        // Seems that target is used, but need to be sure, TODO: Research

        // Find ability or modifier's ability
        if (head.getInstancedModifierId() != 0
                && entity.getInstancedModifiers().containsKey(head.getInstancedModifierId())) {
            ability = entity.getInstancedModifiers().get(head.getInstancedModifierId()).getAbility();
        }

        if (ability == null
                && head.getInstancedAbilityId() != 0
                && (head.getInstancedAbilityId() - 1) < entity.getInstancedAbilities().size()) {
            ability = entity.getInstancedAbilities().get(head.getInstancedAbilityId() - 1);
        }

        if (ability == null) {
            Grasscutter.getLogger()
                    .trace(
                            "Ability not found: ability {} modifier {}",
                            head.getInstancedAbilityId(),
                            head.getInstancedModifierId());
            return;
        }

        // Time to reach the handlers
        var action = ability.getData().localIdToAction.get(head.getLocalId());
        if (action != null) {
            // Executing action
            this.executeAction(ability, action, invoke.getAbilityData(), target);
            return;
        } else {
            var mixin = ability.getData().localIdToMixin.get(head.getLocalId());

            if (mixin != null) {
                executeMixin(ability, mixin, invoke.getAbilityData());

                return;
            }
        }

        Grasscutter.getLogger()
                .trace(
                        "Action or mixin not found: local_id {} ability {} actions to ids {}",
                        head.getLocalId(),
                        ability.getData().abilityName,
                        ability.getData().localIdToAction.toString());
    }

    /**
     * Invoked when a player starts a skill.
     *
     * @param player The player who started the skill.
     * @param skillId The skill ID.
     * @param casterId The caster ID.
     */
    public void onSkillStart(Player player, int skillId, int casterId) {
        // Check if the player matches this player.
        if (player.getUid() != this.player.getUid()) {
            return;
        }

        // Check if the caster matches the player.
        var currentAvatar = player.getTeamManager().getCurrentAvatarEntity();
        if (currentAvatar == null || currentAvatar.getId() != casterId) {
            return;
        }

        var skillData = GameData.getAvatarSkillDataMap().get(skillId);
        if (skillData == null) {
            return;
        }

        // Invoke PlayerUseSkillEvent.
        var event = new PlayerUseSkillEvent(player, skillData, currentAvatar.getAvatar());
        if (!event.call()) return;

        // Check if the skill is an elemental burst.
        if (skillData.getCostElemVal() <= 0) {
            return;
        }

        // Set the player as invulnerable.
        this.abilityInvulnerable = true;
    }

    /**
     * Invoked when a player ends a skill.
     *
     * @param player The player who started the skill.
     */
    public void onSkillEnd(Player player) {
        // Check if the player matches this player.
        if (player.getUid() != this.player.getUid()) {
            return;
        }

        // Check if the player is invulnerable.
        if (!this.abilityInvulnerable) {
            return;
        }

        // Set the player as not invulnerable.
        this.abilityInvulnerable = false;
    }

    private void setAbilityOverrideValue(Ability ability, AbilityScalarValueEntry valueChange) {
        if (valueChange.getValueType() != AbilityScalarType.ABILITY_SCALAR_TYPE_FLOAT) {
            Grasscutter.getLogger().trace("Scalar type not supported: {}", valueChange.getValueType());

            return;
        }

        if (!valueChange.getKey().hasStr()) {
            Grasscutter.getLogger().trace("TODO: Calculate all the ability value hashes");

            return;
        }

        ability.getAbilitySpecials().put(valueChange.getKey().getStr(), valueChange.getFloatValue());
        Grasscutter.getLogger()
                .trace(
                        "Ability {} changed {} to {}",
                        ability.getData().abilityName,
                        valueChange.getKey().getStr(),
                        valueChange.getFloatValue());
    }

    private void handleOverrideParam(AbilityInvokeEntry invoke) throws Exception {
        var entity = this.player.getScene().getEntityById(invoke.getEntityId());
        var head = invoke.getHead();

        if (entity == null) {
            Grasscutter.getLogger().trace("Entity not found: {}", invoke.getEntityId());
            return;
        }

        var instancedAbilityIndex = head.getInstancedAbilityId() - 1;
        if (instancedAbilityIndex >= entity.getInstancedAbilities().size()) {
            Grasscutter.getLogger().trace("Ability not found {}", head.getInstancedAbilityId());
            return;
        }

        var valueChange = AbilityScalarValueEntry.parseFrom(invoke.getAbilityData());

        var ability = entity.getInstancedAbilities().get(instancedAbilityIndex);
        setAbilityOverrideValue(ability, valueChange);
    }

    private void handleReinitOverrideMap(AbilityInvokeEntry invoke) throws Exception {
        var entity = this.player.getScene().getEntityById(invoke.getEntityId());
        var head = invoke.getHead();

        if (entity == null) {
            Grasscutter.getLogger().trace("Entity not found: {}", invoke.getEntityId());
            return;
        }

        var instancedAbilityIndex = head.getInstancedAbilityId() - 1;
        if (instancedAbilityIndex >= entity.getInstancedAbilities().size()) {
            Grasscutter.getLogger().trace("Ability not found {}", head.getInstancedAbilityId());
            return;
        }

        var ability = entity.getInstancedAbilities().get(instancedAbilityIndex);
        var valueChanges = AbilityMetaReInitOverrideMap.parseFrom(invoke.getAbilityData());
        for (var variableChange : valueChanges.getOverrideMapList()) {
            setAbilityOverrideValue(ability, variableChange);
        }
    }

    private void handleModifierChange(AbilityInvokeEntry invoke) throws Exception {
        // TODO:
        var modChange = AbilityMetaModifierChange.parseFrom(invoke.getAbilityData());
        var head = invoke.getHead();

        if (head.getInstancedAbilityId() == 0 || head.getInstancedModifierId() > 2000)
            return; // Error: TODO: display error

        if (head.getIsServerbuffModifier()) {
            // TODO
            Grasscutter.getLogger().trace("TODO: Handle serverbuff modifier");
            return;
        }

        var entity = this.player.getScene().getEntityById(invoke.getEntityId());
        if (entity == null) {
            if (DebugConstants.LOG_ABILITIES) {
                Grasscutter.getLogger().debug("Entity not found: {}", invoke.getEntityId());
            }

            return;
        }

        if (modChange.getAction() == ModifierAction.MODIFIER_ACTION_ADDED) {
            AbilityData instancedAbilityData = null;
            Ability instancedAbility = null;

            if (head.getTargetId() != 0) {
                // Get ability from target entity
                var targetEntity = this.player.getScene().getEntityById(head.getTargetId());
                if (targetEntity != null) {
                    if ((head.getInstancedAbilityId() - 1) < targetEntity.getInstancedAbilities().size()) {
                        instancedAbility =
                                targetEntity.getInstancedAbilities().get(head.getInstancedAbilityId() - 1);
                        if (instancedAbility != null) instancedAbilityData = instancedAbility.getData();
                    }
                }
            }

            if (instancedAbilityData == null) {
                // search on entity base id
                if ((head.getInstancedAbilityId() - 1) < entity.getInstancedAbilities().size()) {
                    instancedAbility = entity.getInstancedAbilities().get(head.getInstancedAbilityId() - 1);
                    if (instancedAbility != null) instancedAbilityData = instancedAbility.getData();
                }
            }

            if (instancedAbilityData == null) {
                // Search for the parent ability

                // TODO: Research about hash
                instancedAbilityData = GameData.getAbilityData(modChange.getParentAbilityName().getStr());
            }

            if (instancedAbilityData == null) {
                Grasscutter.getLogger().trace("No ability found");
                return; // TODO: Display error message
            }

            var modifierArray = instancedAbilityData.modifiers.values().toArray();
            if (modChange.getModifierLocalId() >= modifierArray.length) {
                Grasscutter.getLogger()
                        .trace("Modifier local id {} not found", modChange.getModifierLocalId());
                return;
            }

            var modifierData = (AbilityModifier) modifierArray[modChange.getModifierLocalId()];
            if (entity.getInstancedModifiers().containsKey(head.getInstancedModifierId())) {
                Grasscutter.getLogger()
                        .trace(
                                "Replacing entity {} modifier id {} with ability {} modifier {}",
                                invoke.getEntityId(),
                                head.getInstancedModifierId(),
                                instancedAbilityData.abilityName,
                                modifierData);
            } else {
                Grasscutter.getLogger()
                        .trace(
                                "Adding entity {} modifier id {} with ability {} modifier {}",
                                invoke.getEntityId(),
                                head.getInstancedModifierId(),
                                instancedAbilityData.abilityName,
                                modifierData);
            }

            AbilityModifierController modifier =
                    new AbilityModifierController(instancedAbility, instancedAbilityData, modifierData);

            entity.getInstancedModifiers().put(head.getInstancedModifierId(), modifier);

            // TODO: Add all the ability modifier property change
        } else if (modChange.getAction() == ModifierAction.MODIFIER_ACTION_REMOVED) {
            Grasscutter.getLogger()
                    .trace(
                            "Removed on entity {} modifier id {}: {}",
                            invoke.getEntityId(),
                            head.getInstancedModifierId(),
                            entity.getInstancedModifiers().get(head.getInstancedModifierId()));

            // TODO: Add debug log

            entity.getInstancedModifiers().remove(head.getInstancedModifierId());
        } else {
            // TODO: Display error message
            Grasscutter.getLogger().debug("Unknown action");
        }
    }

    private void handleMixinCostStamina(AbilityInvokeEntry invoke)
            throws InvalidProtocolBufferException {}

    private void handleGenerateElemBall(AbilityInvokeEntry invoke)
            throws InvalidProtocolBufferException {}

    private void handleGlobalFloatValue(AbilityInvokeEntry invoke)
            throws InvalidProtocolBufferException {
        var entity = this.player.getScene().getEntityById(invoke.getEntityId());
        if (entity == null) return;

        var entry = AbilityScalarValueEntry.parseFrom(invoke.getAbilityData());
        if (entry == null || !entry.hasFloatValue()) return;

        String key = null;
        if (entry.getKey().hasStr()) key = entry.getKey().getStr();
        else if (entry.getKey().hasHash())
            key = GameData.getAbilityHashes().get(entry.getKey().getHash());

        if (key == null) return;

        if (key.startsWith("SGV_")) return; // Server does not allow to change this variables I think
        switch (entry.getValueType().getNumber()) {
            case AbilityScalarType.ABILITY_SCALAR_TYPE_FLOAT_VALUE -> {
                if (!Float.isNaN(entry.getFloatValue()))
                    entity.getGlobalAbilityValues().put(key, entry.getFloatValue());
            }
            case AbilityScalarType.ABILITY_SCALAR_TYPE_UINT_VALUE -> entity
                    .getGlobalAbilityValues()
                    .put(key, (float) entry.getUintValue());
            default -> {
                return;
            }
        }

        entity.onAbilityValueUpdate();
    }

    private void invokeAction(
            AbilityModifierAction action, GameEntity target, GameEntity sourceEntity) {}

    private void handleModifierDurabilityChange(AbilityInvokeEntry invoke)
            throws InvalidProtocolBufferException {}

    private void handleAddNewAbility(AbilityInvokeEntry invoke)
            throws InvalidProtocolBufferException {
        var entity = this.player.getScene().getEntityById(invoke.getEntityId());

        if (entity == null) {
            if (DebugConstants.LOG_ABILITIES)
                Grasscutter.getLogger().debug("Entity not found: {}", invoke.getEntityId());
            return;
        }

        var addAbility = AbilityMetaAddAbility.parseFrom(invoke.getAbilityData());
        var abilityName = Ability.getAbilityName(addAbility.getAbility().getAbilityName());
        var ability = GameData.getAbilityData(abilityName);
        if (ability == null) {
            if (DebugConstants.LOG_MISSING_ABILITIES)
                Grasscutter.getLogger().debug("Ability not found: {}", abilityName);
            return;
        }

        entity.getInstancedAbilities().add(new Ability(ability, entity, player));
        if (DebugConstants.LOG_ABILITIES) {
            Grasscutter.getLogger()
                    .debug(
                            "Ability added to entity {} at index {}.",
                            entity.getId(),
                            entity.getInstancedAbilities().size());
        }
    }

    private void handleKillState(AbilityInvokeEntry invoke) throws InvalidProtocolBufferException {
        var scene = this.getPlayer().getScene();
        var entity = scene.getEntityById(invoke.getEntityId());
        if (entity == null) {
            Grasscutter.getLogger()
                    .trace("Entity of ID {} was not found in the scene.", invoke.getEntityId());
            return;
        }

        var killState = AbilityMetaSetKilledState.parseFrom(invoke.getAbilityData());
        if (killState.getKilled()) {
            scene.killEntity(entity);
        } else if (!entity.isAlive()) {
            entity.setFightProperty(
                    FightProperty.FIGHT_PROP_CUR_HP,
                    entity.getFightProperty(FightProperty.FIGHT_PROP_MAX_HP));
        }
    }

    public void addAbilityToEntity(GameEntity entity, String name) {
        AbilityData data = GameData.getAbilityData(name);
        if (data != null) addAbilityToEntity(entity, data);
    }

    public void addAbilityToEntity(GameEntity entity, AbilityData abilityData) {
        var ability = new Ability(abilityData, entity, this.player);
        entity.getInstancedAbilities().add(ability); // This is in order
    }
}

package emu.grasscutter.game.combine;

import emu.grasscutter.Grasscutter;
import emu.grasscutter.data.*;
import emu.grasscutter.data.common.ItemParamData;
import emu.grasscutter.data.excels.CombineData;
import emu.grasscutter.game.inventory.GameItem;
import emu.grasscutter.game.player.Player;
import emu.grasscutter.game.props.ActionReason;
import emu.grasscutter.net.proto.RetcodeOuterClass;
import emu.grasscutter.net.proto.RetcodeOuterClass.Retcode;
import emu.grasscutter.server.game.*;
import emu.grasscutter.server.packet.send.*;
import emu.grasscutter.utils.Utils;
import it.unimi.dsi.fastutil.ints.*;
import java.util.*;

public class CombineManger extends BaseGameSystem {
    private static final Int2ObjectMap<List<Integer>> reliquaryDecomposeData =
            new Int2ObjectOpenHashMap<>();

    public CombineManger(GameServer server) {
        super(server);
    }

    public static void initialize() {
        // Read the data we need for strongbox.
        try {
            DataLoader.loadList("ReliquaryDecompose.json", ReliquaryDecomposeEntry.class)
                    .forEach(
                            entry -> {
                                reliquaryDecomposeData.put(entry.getConfigId(), entry.getItems());
                            });
            Grasscutter.getLogger()
                    .debug("Loaded {} reliquary decompose entries.", reliquaryDecomposeData.size());
        } catch (Exception ex) {
            Grasscutter.getLogger().error("Unable to load reliquary decompose data.", ex);
        }
    }

    public boolean unlockCombineDiagram(Player player, int combineId) {
        if (!player.getUnlockedCombines().add(combineId)) {
            return false; // Already unlocked
        }
        // Tell the client that this diagram is now unlocked and add the unlocked item to the player.
        player.sendPacket(new PacketCombineFormulaDataNotify(combineId));
        return true;
    }

    public CombineResult combineItem(Player player, int cid, int count) {
        // check config exist
        if (!GameData.getCombineDataMap().containsKey(cid)) {
            player.getWorld().getHost().sendPacket(new PacketCombineRsp());
            return null;
        }

        CombineData combineData = GameData.getCombineDataMap().get(cid);

        if (combineData.getPlayerLevel() > player.getLevel()) {
            return null;
        }

        // consume items
        List<ItemParamData> material = new ArrayList<>(combineData.getMaterialItems());
        material.add(new ItemParamData(202, combineData.getScoinCost()));

        boolean success = player.getInventory().payItems(material, count, ActionReason.Combine);

        // abort if not enough material
        if (!success) {
            player.sendPacket(
                    new PacketCombineRsp(RetcodeOuterClass.Retcode.RET_ITEM_COMBINE_COUNT_NOT_ENOUGH_VALUE));
        }

        // make the result
        player
                .getInventory()
                .addItem(combineData.getResultItemId(), combineData.getResultItemCount() * count);

        CombineResult result = new CombineResult();
        result.setMaterial(List.of());
        result.setResult(
                List.of(
                        new ItemParamData(
                                combineData.getResultItemId(), combineData.getResultItemCount() * count)));
        // TODO lucky characters
        result.setExtra(List.of());
        result.setBack(List.of());

        return result;
    }

    public synchronized void decomposeReliquaries(
            Player player, int configId, int count, List<Long> input) {
        // Check if the configId is legal.
        List<Integer> possibleDrops = reliquaryDecomposeData.get(configId);
        if (possibleDrops == null) {
            player.sendPacket(
                    new PacketReliquaryDecomposeRsp(Retcode.RET_RELIQUARY_DECOMPOSE_PARAM_ERROR));
            return;
        }

        // Check if the number of input items matches the output count.
        if (input.size() != count * 3) {
            player.sendPacket(
                    new PacketReliquaryDecomposeRsp(Retcode.RET_RELIQUARY_DECOMPOSE_PARAM_ERROR));
            return;
        }

        // Check if all the input reliquaries actually are in the player's inventory.
        for (long guid : input) {
            if (player.getInventory().getItemByGuid(guid) == null) {
                player.sendPacket(
                        new PacketReliquaryDecomposeRsp(Retcode.RET_RELIQUARY_DECOMPOSE_PARAM_ERROR));
                return;
            }
        }

        // Delete the input reliquaries.
        for (long guid : input) {
            player.getInventory().removeItem(guid);
        }

        // Generate outoput reliquaries.
        List<Long> resultItems = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            int itemId = Utils.drawRandomListElement(possibleDrops);
            GameItem newReliquary = new GameItem(itemId, 1);

            player.getInventory().addItem(newReliquary);
            resultItems.add(newReliquary.getGuid());
        }

        // Send packet.
        player.sendPacket(new PacketReliquaryDecomposeRsp(resultItems));
    }
}
package emu.grasscutter.game.managers;

import static emu.grasscutter.config.Configuration.GAME_OPTIONS;

import emu.grasscutter.game.inventory.GameItem;
import emu.grasscutter.game.player.*;
import emu.grasscutter.game.props.*;
import emu.grasscutter.net.proto.RetcodeOuterClass;
import emu.grasscutter.server.packet.send.*;
import emu.grasscutter.utils.Utils;

public class ResinManager extends BasePlayerManager {
    public static final int MAX_RESIN_BUYING_COUNT = 6;
    public static final int AMOUNT_TO_ADD = 60;
    public static final int[] HCOIN_NUM_TO_BUY_RESIN = new int[] {50, 100, 100, 150, 200, 200};

    public ResinManager(Player player) {
        super(player);
    }

    /********************
     * Change resin.
     ********************/
    public synchronized boolean useResin(int amount) {
        // Check if resin enabled.
        if (!GAME_OPTIONS.resinOptions.resinUsage) {
            return true;
        }

        int currentResin = this.player.getProperty(PlayerProperty.PROP_PLAYER_RESIN);

        // Check if the player has sufficient resin.
        if (currentResin < amount) {
            return false;
        }

        // Deduct the resin from the player.
        int newResin = currentResin - amount;
        this.player.setProperty(PlayerProperty.PROP_PLAYER_RESIN, newResin);

        // Check if this has taken the player under the recharge cap,
        // starting the recharging process.
        if (this.player.getNextResinRefresh() == 0 && newResin < GAME_OPTIONS.resinOptions.cap) {
            int currentTime = Utils.getCurrentSeconds();
            this.player.setNextResinRefresh(currentTime + GAME_OPTIONS.resinOptions.rechargeTime);
        }

        // Send packets.
        this.player.sendPacket(new PacketResinChangeNotify(this.player));

        // Battle Pass trigger
        this.player
                .getBattlePassManager()
                .triggerMission(
                        WatcherTriggerType.TRIGGER_COST_MATERIAL, 106, amount); // Resin item id = 106

        return true;
    }

    public synchronized boolean useCondensedResin(int amount) {
        // Don't deduct if resin disabled.
        if (!GAME_OPTIONS.resinOptions.resinUsage) return true;
        return this.player.getInventory().payItem(220007, amount);
    }

    public synchronized void addResin(int amount) {
        // Check if resin enabled.
        if (!GAME_OPTIONS.resinOptions.resinUsage) {
            return;
        }

        // Add resin.
        int currentResin = this.player.getProperty(PlayerProperty.PROP_PLAYER_RESIN);
        int newResin = currentResin + amount;
        this.player.setProperty(PlayerProperty.PROP_PLAYER_RESIN, newResin);

        // Stop recharging if player is now at or over the cap.
        if (newResin >= GAME_OPTIONS.resinOptions.cap) {
            this.player.setNextResinRefresh(0);
        }

        // Send packets.
        this.player.sendPacket(new PacketResinChangeNotify(this.player));
    }

    /********************
     * Recharge resin.
     ********************/
    public synchronized void rechargeResin() {
        // Check if resin enabled.
        if (!GAME_OPTIONS.resinOptions.resinUsage) {
            return;
        }

        int currentResin = this.player.getProperty(PlayerProperty.PROP_PLAYER_RESIN);
        int currentTime = Utils.getCurrentSeconds();

        // Make sure we are currently in "recharging mode".
        // This is denoted by Player.nextResinRefresh being greater than 0.
        if (this.player.getNextResinRefresh() <= 0) {
            return;
        }

        // Determine if we actually need to recharge yet.
        if (currentTime < this.player.getNextResinRefresh()) {
            return;
        }

        // Calculate how much resin we need to refill and update player.
        // Note that this can be more than one in case the player
        // logged off with uncapped resin and is now logging in again.
        int recharge =
                1
                        + (int)
                                ((currentTime - this.player.getNextResinRefresh())
                                        / GAME_OPTIONS.resinOptions.rechargeTime);
        int newResin = Math.min(GAME_OPTIONS.resinOptions.cap, currentResin + recharge);
        int resinChange = newResin - currentResin;

        this.player.setProperty(PlayerProperty.PROP_PLAYER_RESIN, newResin);

        // Calculate next recharge time.
        // Set to zero to disable recharge (because on/over cap.)
        if (newResin >= GAME_OPTIONS.resinOptions.cap) {
            this.player.setNextResinRefresh(0);
        } else {
            int nextRecharge =
                    this.player.getNextResinRefresh() + resinChange * GAME_OPTIONS.resinOptions.rechargeTime;
            this.player.setNextResinRefresh(nextRecharge);
        }

        // Send packets.
        this.player.sendPacket(new PacketResinChangeNotify(this.player));
    }

    /********************
     * Player login.
     ********************/
    public synchronized void onPlayerLogin() {
        // If resin usage is disabled, set resin to cap.
        if (!GAME_OPTIONS.resinOptions.resinUsage) {
            this.player.setProperty(PlayerProperty.PROP_PLAYER_RESIN, GAME_OPTIONS.resinOptions.cap);
            this.player.setNextResinRefresh(0);
        }

        // In case server administrators change the resin cap while players are capped,
        // we need to restart recharging here.
        int currentResin = this.player.getProperty(PlayerProperty.PROP_PLAYER_RESIN);
        int currentTime = Utils.getCurrentSeconds();

        if (currentResin < GAME_OPTIONS.resinOptions.cap && this.player.getNextResinRefresh() == 0) {
            this.player.setNextResinRefresh(currentTime + GAME_OPTIONS.resinOptions.rechargeTime);
        }

        // Send initial notifications on logon.
        this.player.sendPacket(new PacketResinChangeNotify(this.player));
    }

    public int buy() {
        if (this.player.getResinBuyCount() >= MAX_RESIN_BUYING_COUNT) {
            return RetcodeOuterClass.Retcode.RET_RESIN_BOUGHT_COUNT_EXCEEDED_VALUE;
        }

        var res =
                this.player
                        .getInventory()
                        .payItem(201, HCOIN_NUM_TO_BUY_RESIN[this.player.getResinBuyCount()]);
        if (!res) {
            return RetcodeOuterClass.Retcode.RET_HCOIN_NOT_ENOUGH_VALUE;
        }

        this.player.setResinBuyCount(this.player.getResinBuyCount() + 1);
        this.player.setProperty(PlayerProperty.PROP_PLAYER_WAIT_SUB_HCOIN, 0);
        this.addResin(AMOUNT_TO_ADD);
        this.player.sendPacket(
                new PacketItemAddHintNotify(new GameItem(106, AMOUNT_TO_ADD), ActionReason.BuyResin));

        return 0;
    }
}

package emu.grasscutter.game.managers.cooking;

import emu.grasscutter.data.GameData;
import emu.grasscutter.data.common.ItemParamData;
import emu.grasscutter.data.excels.ItemData;
import emu.grasscutter.game.inventory.GameItem;
import emu.grasscutter.game.player.*;
import emu.grasscutter.game.props.ActionReason;
import emu.grasscutter.net.proto.CookRecipeDataOuterClass;
import emu.grasscutter.net.proto.PlayerCookArgsReqOuterClass.PlayerCookArgsReq;
import emu.grasscutter.net.proto.PlayerCookReqOuterClass.PlayerCookReq;
import emu.grasscutter.net.proto.RetcodeOuterClass.Retcode;
import emu.grasscutter.server.packet.send.*;
import io.netty.util.internal.ThreadLocalRandom;
import java.util.*;

public class CookingManager extends BasePlayerManager {
    private static final int MANUAL_PERFECT_COOK_QUALITY = 3;
    private static Set<Integer> defaultUnlockedRecipies;

    public CookingManager(Player player) {
        super(player);
    }

    public static void initialize() {
        // Initialize the set of recipies that are unlocked by default.
        defaultUnlockedRecipies = new HashSet<>();

        for (var recipe : GameData.getCookRecipeDataMap().values()) {
            if (recipe.isDefaultUnlocked()) {
                defaultUnlockedRecipies.add(recipe.getId());
            }
        }
    }

    /********************
     * Unlocking for recipies.
     ********************/
    public boolean unlockRecipe(int id) {
        if (this.player.getUnlockedRecipies().containsKey(id)) {
            return false; // Recipe already unlocked
        }
        // Tell the client that this blueprint is now unlocked and add the unlocked item to the player.
        this.player.getUnlockedRecipies().put(id, 0);
        this.player.sendPacket(new PacketCookRecipeDataNotify(id));

        return true;
    }

    /********************
     * Perform cooking.
     ********************/
    private double getSpecialtyChance(ItemData cookedItem) {
        // Chances taken from the Wiki.
        return switch (cookedItem.getRankLevel()) {
            case 1 -> 0.25;
            case 2 -> 0.2;
            case 3 -> 0.15;
            default -> 0;
        };
    }

    public void handlePlayerCookReq(PlayerCookReq req) {
        // Get info from the request.
        int recipeId = req.getRecipeId();
        int quality = req.getQteQuality();
        int count = req.getCookCount();
        int avatar = req.getAssistAvatar();

        // Get recipe data.
        var recipeData = GameData.getCookRecipeDataMap().get(recipeId);
        if (recipeData == null) {
            this.player.sendPacket(new PacketPlayerCookRsp(Retcode.RET_FAIL));
            return;
        }

        // Get proficiency for player.
        int proficiency = this.player.getUnlockedRecipies().getOrDefault(recipeId, 0);

        // Try consuming materials.
        boolean success =
                player.getInventory().payItems(recipeData.getInputVec(), count, ActionReason.Cook);
        if (!success) {
            this.player.sendPacket(new PacketPlayerCookRsp(Retcode.RET_FAIL));
        }

        // Get result item information.
        int qualityIndex = quality == 0 ? 2 : quality - 1;

        ItemParamData resultParam = recipeData.getQualityOutputVec().get(qualityIndex);
        ItemData resultItemData = GameData.getItemDataMap().get(resultParam.getItemId());

        // Handle character's specialties.
        int specialtyCount = 0;
        double specialtyChance = this.getSpecialtyChance(resultItemData);

        var bonusData = GameData.getCookBonusDataMap().get(avatar);
        if (bonusData != null && recipeId == bonusData.getRecipeId()) {
            // Roll for specialy replacements.
            for (int i = 0; i < count; i++) {
                if (ThreadLocalRandom.current().nextDouble() <= specialtyChance) {
                    specialtyCount++;
                }
            }
        }

        // Obtain results.
        List<GameItem> cookResults = new ArrayList<>();

        int normalCount = count - specialtyCount;
        GameItem cookResultNormal = new GameItem(resultItemData, resultParam.getCount() * normalCount);
        cookResults.add(cookResultNormal);
        this.player.getInventory().addItem(cookResultNormal);

        if (specialtyCount > 0) {
            ItemData specialtyItemData = GameData.getItemDataMap().get(bonusData.getReplacementItemId());
            GameItem cookResultSpecialty =
                    new GameItem(specialtyItemData, resultParam.getCount() * specialtyCount);
            cookResults.add(cookResultSpecialty);
            this.player.getInventory().addItem(cookResultSpecialty);
        }

        // Increase player proficiency, if this was a manual perfect cook.
        if (quality == MANUAL_PERFECT_COOK_QUALITY) {
            proficiency = Math.min(proficiency + 1, recipeData.getMaxProficiency());
            this.player.getUnlockedRecipies().put(recipeId, proficiency);
        }

        // Send response.
        this.player.sendPacket(
                new PacketPlayerCookRsp(cookResults, quality, count, recipeId, proficiency));
    }

    /********************
     * Cooking arguments.
     ********************/
    public void handleCookArgsReq(PlayerCookArgsReq req) {
        this.player.sendPacket(new PacketPlayerCookArgsRsp());
    }

    /********************
     * Notify unlocked recipies.
     ********************/
    private void addDefaultUnlocked() {
        // Get recipies that are already unlocked.
        var unlockedRecipies = this.player.getUnlockedRecipies();

        // Get recipies that should be unlocked by default but aren't.
        var additionalRecipies = new HashSet<>(defaultUnlockedRecipies);
        additionalRecipies.removeAll(unlockedRecipies.keySet());

        // Add them to the player.
        for (int id : additionalRecipies) {
            unlockedRecipies.put(id, 0);
        }
    }

    public void sendCookDataNotify() {
        // Default unlocked recipes to player if they don't have them yet.
        this.addDefaultUnlocked();

        // Get unlocked recipes.
        var unlockedRecipes = this.player.getUnlockedRecipies();

        // Construct CookRecipeData protos.
        List<CookRecipeDataOuterClass.CookRecipeData> data = new ArrayList<>();
        unlockedRecipes.forEach(
                (recipeId, proficiency) ->
                        data.add(
                                CookRecipeDataOuterClass.CookRecipeData.newBuilder()
                                        .setRecipeId(recipeId)
                                        .setProficiency(proficiency)
                                        .build()));

        // Send packet.
        this.player.sendPacket(new PacketCookDataNotify(data));
    }
}