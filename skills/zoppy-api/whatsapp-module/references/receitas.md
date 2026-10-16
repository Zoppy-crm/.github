# Receitas

Esqueletos curtos no formato do envio de template, de fora para dentro. Nomes reais do módulo;
corpo reduzido ao essencial.

## Fachada pública e Command

```ts
export interface SendTemplateCommand {
    readonly tenantId: string;
    readonly to: string;
    readonly templateId: string;
    readonly variables: Readonly<Record<string, string>>;
    readonly correlation: { readonly type: string; readonly id: string };
    readonly idempotencyKey: string;
}

export interface MessagingFacade {
    sendTemplate(command: SendTemplateCommand): Promise<{ readonly messageId: string }>;
}

export const MESSAGING_FACADE = Symbol('MESSAGING_FACADE');
```

Arquivo: `public/messaging.facade.ts`. Command só com primitivos: quem chama não conhece os objetos de valor.

## Implementação da fachada e mapper (access)

```ts
export function toSendTemplateInput(command: SendTemplateCommand): SendTemplateInput {
    return {
        to: PhoneE164.parse(command.to),
        templateId: TemplateId.of(command.templateId),
        variables: TemplateVariables.of(command.variables),
        correlation: Correlation.of(command.correlation.type, command.correlation.id),
    };
}

@Injectable()
export class MessagingFacadeImpl implements MessagingFacade {
    constructor(private readonly messaging: MessagingApplication) {}

    public async sendTemplate(command: SendTemplateCommand): Promise<{ readonly messageId: string }> {
        const message = await this.messaging.sendTemplate(toSendTemplateInput(command));
        return { messageId: message.id };
    }
}
```

## Contrato entre submódulos (api)

```ts
export interface ContactForSending {
    readonly id: string;
    readonly phone: string;
    readonly isBlocked: boolean;
    readonly windowOpenUntil: Date | null;
}

export interface ContactsApi {
    findForSending(tenantId: string, phone: string): Promise<ContactForSending>;
    block(tenantId: string, phone: string): Promise<void>;
}

export const CONTACTS_API = Symbol('CONTACTS_API');
```

## Application

```ts
@Injectable()
export class MessagingApplication {
    constructor(
        @Inject(ACCOUNTS_API) private readonly accounts: AccountsApi,
        @Inject(CONTACTS_API) private readonly contacts: ContactsApi,
        @Inject(TEMPLATES_API) private readonly templates: TemplatesApi,
        @Inject(MESSAGE_REPOSITORY) private readonly messages: MessageRepository,
        @Inject(DISPATCH_QUEUE) private readonly dispatchQueue: DispatchQueue,
    ) {}

    public async sendTemplate(input: SendTemplateInput): Promise<Message> {
        const sending = await this.loadSending(input);
        const message = Message.createTemplate(sending, input.variables, input.correlation);
        await this.messages.save(message);
        await this.dispatchQueue.schedule(message.id, sending.account.sendRate);
        return message;
    }
}
```

O limite de 4 parâmetros vale para métodos. O construtor tem limite próprio de 6 dependências; acima disso, divida o caso de uso.

## Agregado com a regra de criação

```ts
export class Message {
    public static createTemplate(sending: Sending, variables: TemplateVariables, correlation: Correlation): Message {
        Message.assertCanSend(sending);
        return new Message(MessageId.new(), sending, variables, correlation, MessageStatus.PENDING);
    }

    public markSent(wamId: WamId, at: Date): void {
        this.status = this.status.transitionTo(MessageStatus.SENT);
        this.wamId = wamId;
        this.sentAt = at;
    }
}
```

## Porta e adaptador

```ts
export interface MetaGateway {
    sendTemplate(message: OutgoingTemplate): Promise<WamId>;
}

@Injectable()
export class WhatsappV2MetaGateway implements MetaGateway {
    public async sendTemplate(message: OutgoingTemplate): Promise<WamId> { … }
}
```

## Repositório e mapper

```ts
@Injectable()
export class SequelizeMessageRepository implements MessageRepository {
    public async save(message: Message): Promise<void> {
        await WppMessage.upsert(MessageMapper.toRow(message));
    }

    public async findById(tenantId: string, id: MessageId): Promise<Message | null> {
        const row = await WppMessage.findOne({ where: { id: id.value, companyId: tenantId } });
        return row ? MessageMapper.toDomain(row) : null;
    }
}
```

`MessageMapper.toRow` preenche todas as colunas que o código legado ainda lê.

## Fila (porta no domain, adaptador na infrastructure, processor no access)

```ts
export interface DispatchQueue {
    schedule(messageId: MessageId, rate: SendRate): Promise<void>;
}

@Injectable()
export class BullMqDispatchQueue implements DispatchQueue {
    constructor(@InjectRingQueue(MessagingQueue.DISPATCH) private readonly queue: Queue) {}

    public async schedule(messageId: MessageId, rate: SendRate): Promise<void> {
        await this.queue.add(MessagingQueue.DISPATCH, envelope({ messageId: messageId.value }), {
            jobId: messageId.value,
        });
    }
}

@Processor(MessagingQueue.DISPATCH)
export class DispatchMessageProcessor extends WhatsappProcessorBase<{ messageId: string }> {
    constructor(private readonly messaging: MessagingApplication) { super(); }

    protected async handle(data: { messageId: string }): Promise<void> {
        await this.messaging.dispatch(MessageId.of(data.messageId));
    }
}
```

## Evento publicado e assinatura no CRM

```ts
export interface MessageReceivedV1 {
    readonly messageId: string;
    readonly contactId: string;
    readonly phoneNumberId: string;
    readonly receivedAt: string;
}

await this.events.publish(WhatsappEvent.MESSAGE_RECEIVED_V1, payload);

@HandlesEvent(WhatsappEvent.MESSAGE_RECEIVED_V1)
export class ReopenRoomOnMessageReceived { … }
```

O tipo do evento mora em `public/events/`. Ver [filas-e-eventos.md](filas-e-eventos.md).

## Registro do submódulo

```ts
@Module({
    providers: [
        MessagingApplication,
        { provide: MESSAGE_REPOSITORY, useClass: SequelizeMessageRepository },
        { provide: META_GATEWAY, useClass: WhatsappV2MetaGateway },
        { provide: DISPATCH_QUEUE, useClass: BullMqDispatchQueue },
        { provide: MESSAGING_FACADE, useClass: MessagingFacadeImpl },
    ],
    exports: [MESSAGING_FACADE],
})
export class MessagingModule {}
```
